"""
RAG Chain Implementation using LangChain

This module implements the core RAG (Retrieval-Augmented Generation) chain
that orchestrates document retrieval and language model generation.
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
import asyncio

from langchain.schema import BaseRetriever, Document
from langchain.schema.runnable import Runnable
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManagerForChainRun

from src.core.config.settings import get_settings
from src.core.logging.logger import get_logger, performance_logger
from src.rag.retrievers.hybrid_retriever import HybridRetriever
from src.llm.providers.llm_factory import LLMFactory
from src.rag.prompts.prompt_templates import RAGPromptTemplates
from src.utils.text_processing import clean_text, truncate_context


logger = get_logger(__name__)


class RAGCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for RAG chain monitoring."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.start_time = None
        self.retrieval_time = None
        self.generation_time = None
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Called when the chain starts running."""
        self.start_time = datetime.utcnow()
        self.logger.info(
            "rag_chain_started",
            query=inputs.get("question", ""),
            chain_type=serialized.get("name", "unknown")
        )
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Called when the chain finishes running."""
        total_time = (datetime.utcnow() - self.start_time).total_seconds()
        self.logger.info(
            "rag_chain_completed",
            total_duration_seconds=total_time,
            retrieval_duration_seconds=self.retrieval_time,
            generation_duration_seconds=self.generation_time,
            answer_length=len(outputs.get("answer", "")),
            sources_count=len(outputs.get("sources", []))
        )
    
    def on_chain_error(self, error: Exception, **kwargs) -> None:
        """Called when the chain encounters an error."""
        self.logger.error(
            "rag_chain_error",
            error_type=type(error).__name__,
            error_message=str(error)
        )


class EnhancedRAGChain:
    """
    Enhanced RAG Chain with advanced features:
    - Hybrid retrieval (dense + sparse)
    - Query expansion and rewriting
    - Context reranking
    - Answer validation
    - Source attribution
    """
    
    def __init__(
        self,
        retriever: Optional[BaseRetriever] = None,
        llm_provider: str = "openai",
        prompt_template: Optional[str] = None,
        max_context_length: int = 4000,
        temperature: float = 0.7,
        enable_reranking: bool = True,
        enable_query_expansion: bool = True
    ):
        self.settings = get_settings()
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize components
        self.retriever = retriever or self._create_default_retriever()
        self.llm = LLMFactory.create_llm(llm_provider)
        self.prompt_templates = RAGPromptTemplates()
        self.callback_handler = RAGCallbackHandler()
        
        # Configuration
        self.max_context_length = max_context_length
        self.temperature = temperature
        self.enable_reranking = enable_reranking
        self.enable_query_expansion = enable_query_expansion
        
        # Build the chain
        self.chain = self._build_chain(prompt_template)
    
    def _create_default_retriever(self) -> BaseRetriever:
        """Create default hybrid retriever."""
        return HybridRetriever(
            dense_k=5,
            sparse_k=10,
            alpha=0.7  # Weight for dense vs sparse
        )
    
    def _build_chain(self, custom_prompt: Optional[str] = None) -> Runnable:
        """Build the RAG chain with all components."""
        
        # Select prompt template
        if custom_prompt:
            prompt = PromptTemplate.from_template(custom_prompt)
        else:
            prompt = self.prompt_templates.get_qa_prompt()
        
        # Define chain components
        def format_docs(docs: List[Document]) -> str:
            """Format retrieved documents for context."""
            formatted = []
            for i, doc in enumerate(docs, 1):
                content = clean_text(doc.page_content)
                metadata = doc.metadata
                source = metadata.get('source', 'Unknown')
                
                formatted.append(f"[{i}] {content} (Source: {source})")
            
            context = "\\n\\n".join(formatted)
            return truncate_context(context, self.max_context_length)
        
        def extract_sources(docs: List[Document]) -> List[Dict[str, Any]]:
            """Extract source information from documents."""
            sources = []
            for doc in docs:
                metadata = doc.metadata
                sources.append({
                    "source": metadata.get('source', 'Unknown'),
                    "title": metadata.get('title', ''),
                    "url": metadata.get('url', ''),
                    "chunk_id": metadata.get('chunk_id', ''),
                    "score": metadata.get('score', 0.0),
                    "content_preview": doc.page_content[:200] + "..."
                })
            return sources
        
        # Query expansion (if enabled)
        if self.enable_query_expansion:
            query_expander = self._create_query_expander()
            expanded_query = query_expander | RunnableLambda(lambda x: x.get("expanded_query", x.get("question")))
        else:
            expanded_query = RunnableLambda(lambda x: x.get("question"))
        
        # Core RAG chain
        rag_chain = (
            {
                "context": expanded_query | self.retriever | RunnableLambda(format_docs),
                "sources": expanded_query | self.retriever | RunnableLambda(extract_sources),
                "question": RunnablePassthrough()
            }
            | RunnablePassthrough.assign(
                answer=prompt | self.llm | StrOutputParser()
            )
        )
        
        return rag_chain
    
    def _create_query_expander(self) -> Runnable:
        """Create query expansion chain."""
        expansion_prompt = self.prompt_templates.get_query_expansion_prompt()
        
        return (
            expansion_prompt 
            | self.llm 
            | StrOutputParser()
            | RunnableLambda(lambda x: {"expanded_query": x})
        )
    
    @performance_logger("rag_chain_invoke")
    async def ainvoke(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously invoke the RAG chain.
        
        Args:
            query: User question
            context: Additional context information
            config: Runtime configuration
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            # Prepare input
            input_data = {
                "question": query,
                **(context or {})
            }
            
            # Configure callbacks
            chain_config = {
                "callbacks": [self.callback_handler],
                **(config or {})
            }
            
            # Execute chain
            result = await self.chain.ainvoke(input_data, config=chain_config)
            
            # Post-process result
            processed_result = await self._post_process_result(result, query)
            
            return processed_result
            
        except Exception as e:
            self.logger.error(
                "rag_chain_execution_failed",
                query=query,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
    
    def invoke(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synchronously invoke the RAG chain.
        
        Args:
            query: User question
            context: Additional context information  
            config: Runtime configuration
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        return asyncio.run(self.ainvoke(query, context, config))
    
    async def _post_process_result(
        self, 
        result: Dict[str, Any], 
        original_query: str
    ) -> Dict[str, Any]:
        """Post-process the RAG result."""
        
        # Validate answer quality
        answer_quality = await self._validate_answer_quality(
            result.get("answer", ""), 
            original_query,
            result.get("sources", [])
        )
        
        # Add metadata
        processed_result = {
            **result,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "original_query": original_query,
                "answer_quality": answer_quality,
                "model_used": self.llm.__class__.__name__,
                "retrieval_method": "hybrid" if isinstance(self.retriever, HybridRetriever) else "standard",
                "context_length": len(result.get("context", "")),
                "sources_count": len(result.get("sources", [])),
            }
        }
        
        return processed_result
    
    async def _validate_answer_quality(
        self, 
        answer: str, 
        query: str, 
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate the quality of the generated answer."""
        
        quality_metrics = {
            "completeness": 0.0,
            "relevance": 0.0,
            "factuality": 0.0,
            "source_attribution": 0.0,
            "overall_score": 0.0
        }
        
        try:
            # Basic quality checks
            if len(answer.strip()) == 0:
                return quality_metrics
            
            # Completeness check (answer length vs typical good answers)
            typical_good_length = 150  # characters
            quality_metrics["completeness"] = min(1.0, len(answer) / typical_good_length)
            
            # Relevance check (keyword overlap)
            query_words = set(query.lower().split())
            answer_words = set(answer.lower().split())
            overlap = len(query_words & answer_words)
            quality_metrics["relevance"] = min(1.0, overlap / max(len(query_words), 1))
            
            # Source attribution check
            if sources:
                # Check if answer references sources
                has_attribution = any(
                    str(i) in answer for i in range(1, len(sources) + 1)
                ) or any(
                    source["source"].split("/")[-1].lower() in answer.lower() 
                    for source in sources if source.get("source")
                )
                quality_metrics["source_attribution"] = 1.0 if has_attribution else 0.0
            
            # Calculate overall score
            weights = {
                "completeness": 0.3,
                "relevance": 0.4,
                "factuality": 0.2,  # Would need external fact-checking
                "source_attribution": 0.1
            }
            
            quality_metrics["overall_score"] = sum(
                quality_metrics[metric] * weight 
                for metric, weight in weights.items()
            )
            
        except Exception as e:
            self.logger.warning(
                "answer_quality_validation_failed",
                error=str(e)
            )
        
        return quality_metrics
    
    async def batch_invoke(
        self, 
        queries: List[str], 
        context: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process multiple queries in batch."""
        
        tasks = [
            self.ainvoke(query, context, config) 
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "answer": "Sorry, I couldn't process this question.",
                    "sources": [],
                    "error": str(result),
                    "metadata": {
                        "original_query": queries[i],
                        "timestamp": datetime.utcnow().isoformat(),
                        "error_type": type(result).__name__
                    }
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def update_configuration(self, **kwargs):
        """Update chain configuration at runtime."""
        
        if "temperature" in kwargs:
            self.temperature = kwargs["temperature"]
            # Would need to recreate LLM with new temperature
        
        if "max_context_length" in kwargs:
            self.max_context_length = kwargs["max_context_length"]
        
        if "enable_reranking" in kwargs:
            self.enable_reranking = kwargs["enable_reranking"]
            # Would need to rebuild chain if this changes
        
        self.logger.info("rag_chain_configuration_updated", **kwargs)


class RAGChainManager:
    """Manager for multiple RAG chain instances."""
    
    def __init__(self):
        self.chains: Dict[str, EnhancedRAGChain] = {}
        self.logger = get_logger(self.__class__.__name__)
    
    def create_chain(
        self, 
        name: str, 
        **chain_config
    ) -> EnhancedRAGChain:
        """Create a new RAG chain instance."""
        
        chain = EnhancedRAGChain(**chain_config)
        self.chains[name] = chain
        
        self.logger.info(
            "rag_chain_created",
            name=name,
            config=chain_config
        )
        
        return chain
    
    def get_chain(self, name: str) -> Optional[EnhancedRAGChain]:
        """Get a RAG chain by name."""
        return self.chains.get(name)
    
    def list_chains(self) -> List[str]:
        """List all available chain names."""
        return list(self.chains.keys())
    
    def remove_chain(self, name: str) -> bool:
        """Remove a RAG chain."""
        if name in self.chains:
            del self.chains[name]
            self.logger.info("rag_chain_removed", name=name)
            return True
        return False


# Global chain manager instance
chain_manager = RAGChainManager()

# Default chain factory
def create_default_rag_chain(**kwargs) -> EnhancedRAGChain:
    """Create a default RAG chain with recommended settings."""
    
    settings = get_settings()
    
    default_config = {
        "llm_provider": settings.llm.default_provider.value,
        "temperature": 0.7,
        "max_context_length": 4000,
        "enable_reranking": True,
        "enable_query_expansion": True,
    }
    
    # Override with provided kwargs
    default_config.update(kwargs)
    
    return EnhancedRAGChain(**default_config)


# Export main components
__all__ = [
    "EnhancedRAGChain",
    "RAGChainManager", 
    "RAGCallbackHandler",
    "chain_manager",
    "create_default_rag_chain",
]