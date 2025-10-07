"""
Streamlit Interface for RAG Knowledge System Chatbot

This module provides a modern, interactive web interface for the RAG chatbot
with real-time responses, source citations, and advanced features.
"""

import os
import sys
import time
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.rag.chains.rag_chain import create_default_rag_chain
from src.core.config.settings import get_settings
from src.core.logging.logger import get_logger, set_correlation_id
from src.utils.text_processing import highlight_sources

# Configure page
st.set_page_config(
    page_title="RAG Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logging
logger = get_logger(__name__)
settings = get_settings()


class ChatInterface:
    """Main chat interface class."""
    
    def __init__(self):
        self.initialize_session_state()
        self.setup_sidebar()
        
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "¡Hola! Soy tu asistente de conocimiento RAG. ¿En qué puedo ayudarte hoy?",
                    "timestamp": datetime.now().isoformat(),
                    "sources": [],
                    "metadata": {}
                }
            ]
        
        if "rag_chain" not in st.session_state:
            with st.spinner("Inicializando sistema RAG..."):
                st.session_state.rag_chain = create_default_rag_chain()
        
        if "conversation_id" not in st.session_state:
            st.session_state.conversation_id = set_correlation_id()
        
        if "query_count" not in st.session_state:
            st.session_state.query_count = 0
        
        if "total_response_time" not in st.session_state:
            st.session_state.total_response_time = 0.0
        
        if "settings" not in st.session_state:
            st.session_state.settings = {
                "temperature": 0.7,
                "max_context_length": 4000,
                "enable_sources": True,
                "enable_quality_metrics": True,
                "response_style": "balanced"
            }
    
    def setup_sidebar(self):
        """Setup the sidebar with controls and information."""
        
        with st.sidebar:
            st.header("🛠️ Configuración")
            
            # Model settings
            st.subheader("Modelo")
            st.session_state.settings["temperature"] = st.slider(
                "Temperatura",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.settings["temperature"],
                step=0.1,
                help="Controla la creatividad de las respuestas"
            )
            
            st.session_state.settings["max_context_length"] = st.slider(
                "Longitud máxima del contexto",
                min_value=1000,
                max_value=8000,
                value=st.session_state.settings["max_context_length"],
                step=500,
                help="Cantidad máxima de texto de contexto"
            )
            
            # Display settings
            st.subheader("Visualización")
            st.session_state.settings["enable_sources"] = st.checkbox(
                "Mostrar fuentes",
                value=st.session_state.settings["enable_sources"],
                help="Mostrar fuentes y referencias en las respuestas"
            )
            
            st.session_state.settings["enable_quality_metrics"] = st.checkbox(
                "Mostrar métricas de calidad",
                value=st.session_state.settings["enable_quality_metrics"],
                help="Mostrar métricas de calidad de las respuestas"
            )
            
            st.session_state.settings["response_style"] = st.selectbox(
                "Estilo de respuesta",
                ["conciso", "balanced", "detallado"],
                index=["conciso", "balanced", "detallado"].index(st.session_state.settings["response_style"]),
                help="Estilo de las respuestas del asistente"
            )
            
            # Statistics
            add_vertical_space(2)
            st.subheader("📊 Estadísticas")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Consultas", st.session_state.query_count)
            with col2:
                avg_time = (
                    st.session_state.total_response_time / max(st.session_state.query_count, 1)
                    if st.session_state.query_count > 0
                    else 0
                )
                st.metric("Tiempo promedio", f"{avg_time:.2f}s")
            
            # Reset button
            add_vertical_space(2)
            if st.button("🗑️ Limpiar conversación", use_container_width=True):
                self.reset_conversation()
            
            # Export button
            if st.button("💾 Exportar conversación", use_container_width=True):
                self.export_conversation()
    
    def reset_conversation(self):
        """Reset the conversation."""
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "¡Conversación reiniciada! ¿En qué puedo ayudarte?",
                "timestamp": datetime.now().isoformat(),
                "sources": [],
                "metadata": {}
            }
        ]
        st.session_state.query_count = 0
        st.session_state.total_response_time = 0.0
        st.session_state.conversation_id = set_correlation_id()
        st.rerun()
    
    def export_conversation(self):
        """Export conversation to JSON."""
        export_data = {
            "conversation_id": st.session_state.conversation_id,
            "timestamp": datetime.now().isoformat(),
            "messages": st.session_state.messages,
            "statistics": {
                "query_count": st.session_state.query_count,
                "total_response_time": st.session_state.total_response_time,
                "settings": st.session_state.settings
            }
        }
        
        st.download_button(
            label="Descargar JSON",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name=f"conversacion_{st.session_state.conversation_id[:8]}.json",
            mime="application/json"
        )
    
    def display_message(self, message_data: Dict[str, Any], index: int):
        """Display a single message with enhanced formatting."""
        
        role = message_data["role"]
        content = message_data["content"]
        timestamp = message_data.get("timestamp", "")
        sources = message_data.get("sources", [])
        metadata = message_data.get("metadata", {})
        
        # Create message container
        with st.container():
            if role == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                    <div style="background-color: #0084ff; color: white; padding: 10px 15px; 
                                border-radius: 18px; max-width: 70%; word-wrap: break-word;">
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            else:  # assistant
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                    <div style="background-color: #f1f3f4; color: #202124; padding: 15px; 
                                border-radius: 18px; max-width: 85%; word-wrap: break-word;
                                box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        {content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show sources if enabled and available
                if st.session_state.settings["enable_sources"] and sources:
                    self.display_sources(sources)
                
                # Show quality metrics if enabled and available
                if (st.session_state.settings["enable_quality_metrics"] and 
                    metadata and "answer_quality" in metadata):
                    self.display_quality_metrics(metadata["answer_quality"])
                
                # Show response metadata
                if metadata:
                    with st.expander("📋 Detalles de respuesta", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if "model_used" in metadata:
                                st.text(f"Modelo: {metadata['model_used']}")
                            if "context_length" in metadata:
                                st.text(f"Contexto: {metadata['context_length']} chars")
                        
                        with col2:
                            if "sources_count" in metadata:
                                st.text(f"Fuentes: {metadata['sources_count']}")
                            if "retrieval_method" in metadata:
                                st.text(f"Retrieval: {metadata['retrieval_method']}")
                        
                        with col3:
                            st.text(f"Timestamp: {timestamp[:19]}")
    
    def display_sources(self, sources: List[Dict[str, Any]]):
        """Display source information."""
        
        with st.expander(f"📚 Fuentes ({len(sources)})", expanded=False):
            for i, source in enumerate(sources, 1):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    **[{i}] {source.get('title', 'Sin título')}**  
                    *{source.get('source', 'Fuente desconocida')}*  
                    {source.get('content_preview', '')}
                    """)
                
                with col2:
                    if 'score' in source:
                        score = source['score']
                        color = "green" if score > 0.8 else "orange" if score > 0.6 else "red"
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <div style="color: {color}; font-weight: bold;">
                                {score:.2f}
                            </div>
                            <small>Relevancia</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                if i < len(sources):  # Add separator except for last item
                    st.markdown("---")
    
    def display_quality_metrics(self, quality_metrics: Dict[str, float]):
        """Display answer quality metrics."""
        
        with st.expander("📊 Métricas de calidad", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # Overall score gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=quality_metrics.get("overall_score", 0) * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Calidad General"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig.update_layout(height=200)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Individual metrics
                metrics = [
                    ("Completitud", quality_metrics.get("completeness", 0)),
                    ("Relevancia", quality_metrics.get("relevance", 0)),
                    ("Factualidad", quality_metrics.get("factuality", 0)),
                    ("Atribución", quality_metrics.get("source_attribution", 0))
                ]
                
                for metric_name, value in metrics:
                    progress_color = "#1f77b4"  # Default blue
                    if value < 0.5:
                        progress_color = "#d62728"  # Red
                    elif value < 0.8:
                        progress_color = "#ff7f0e"  # Orange
                    else:
                        progress_color = "#2ca02c"  # Green
                    
                    st.markdown(f"""
                    <div style="margin: 5px 0;">
                        <div style="display: flex; justify-content: space-between;">
                            <span>{metric_name}</span>
                            <span>{value:.1%}</span>
                        </div>
                        <div style="background-color: #e0e0e0; border-radius: 5px; height: 10px;">
                            <div style="background-color: {progress_color}; width: {value*100:.1f}%; 
                                        height: 100%; border-radius: 5px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query through RAG chain."""
        
        start_time = time.time()
        
        try:
            # Update chain configuration
            st.session_state.rag_chain.update_configuration(
                temperature=st.session_state.settings["temperature"],
                max_context_length=st.session_state.settings["max_context_length"]
            )
            
            # Process query
            response = await st.session_state.rag_chain.ainvoke(query)
            
            # Update statistics
            response_time = time.time() - start_time
            st.session_state.query_count += 1
            st.session_state.total_response_time += response_time
            
            # Log the interaction
            logger.info(
                "streamlit_query_processed",
                query=query,
                response_time=response_time,
                query_count=st.session_state.query_count,
                sources_count=len(response.get("sources", [])),
                conversation_id=st.session_state.conversation_id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "streamlit_query_error",
                query=query,
                error=str(e),
                error_type=type(e).__name__
            )
            
            return {
                "answer": f"Lo siento, ocurrió un error al procesar tu pregunta: {str(e)}",
                "sources": [],
                "metadata": {
                    "error": True,
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def run(self):
        """Run the main chat interface."""
        
        # Header
        colored_header(
            label="🧠 RAG Knowledge Assistant",
            description="Tu asistente inteligente basado en conocimiento especializado",
            color_name="blue-70"
        )
        
        # Display chat messages
        chat_container = st.container()
        
        with chat_container:
            for i, message_data in enumerate(st.session_state.messages):
                self.display_message(message_data, i)
        
        # Chat input
        with st.container():
            user_input = st.chat_input(
                placeholder="Escribe tu pregunta aquí...",
                key="chat_input"
            )
            
            if user_input:
                # Add user message
                user_message = {
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat(),
                    "sources": [],
                    "metadata": {}
                }
                st.session_state.messages.append(user_message)
                
                # Process query and get response
                with st.spinner("🤔 Procesando tu pregunta..."):
                    response = asyncio.run(self.process_query(user_input))
                
                # Add assistant response
                assistant_message = {
                    "role": "assistant",
                    "content": response.get("answer", "No pude generar una respuesta."),
                    "timestamp": datetime.now().isoformat(),
                    "sources": response.get("sources", []),
                    "metadata": response.get("metadata", {})
                }
                st.session_state.messages.append(assistant_message)
                
                # Rerun to show new messages
                st.rerun()
        
        # Footer with system information
        with st.expander("ℹ️ Información del sistema", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.text(f"Versión: 1.0.0")
                st.text(f"Entorno: {settings.environment.value}")
            
            with col2:
                st.text(f"LLM: {settings.llm.default_provider.value}")
                st.text(f"Vector DB: {settings.vector_store.provider.value}")
            
            with col3:
                st.text(f"Conversación: {st.session_state.conversation_id[:8]}")
                st.text(f"Uptime: {time.time():.0f}s")


def main():
    """Main application entry point."""
    try:
        chat_interface = ChatInterface()
        chat_interface.run()
        
    except Exception as e:
        st.error(f"Error initializing application: {str(e)}")
        logger.error(
            "streamlit_app_initialization_error",
            error=str(e),
            error_type=type(e).__name__
        )


if __name__ == "__main__":
    main()