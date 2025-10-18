"""
Proveedor de asistente para modelos Ollama.
Implementa la interfaz AssistantInterface para interactuar con Ollama usando langchain_ollama.
"""

from src.core.logging.logger import get_logger
from src.core.prompts import PROMPTS
from .base import AssistantInterface

from langchain_ollama import ChatOllama


class OllamaAssistant(AssistantInterface):
    """
    Asistente basado en modelos Ollama usando langchain_ollama.
    Modelos soportados: 'qwen3:1.7b', 'gemma3:1b'.
    """

    def __init__(self, model_name: str = "gemma3:1b", temperature: float = 0.7, top_k: int = 40):
        if model_name not in ("qwen3:1.7b", "gemma3:1b"):
            raise ValueError(
                "Solo se permiten los modelos 'qwen3:1.7b' o 'gemma3:1b' para OllamaAssistant."
            )
        self.model_name = model_name
        self.context = {}
        self.llm = ChatOllama(model=model_name, temperature=temperature, top_k=top_k)
        self.logger = get_logger(__name__)

    def generate_response(self, prompt, context):
        """
        Genera una respuesta real usando langchain_ollama.ChatOllama.
        Args:
            prompt (str): Pregunta del usuario.
        Returns:
            str: Respuesta generada por el modelo Ollama.
        """
        # Construye lista de mensajes tipo chat
        messages = []
        messages.append(("system", context))
        messages.append(("human", str(prompt)))
        self.logger.debug(f"Mensajes enviados a Ollama ({self.model_name}): {messages}")
        response = self.llm.invoke(messages)
        self.logger.info(f"Respuesta generada por Ollama ({self.model_name}): {response}")
        return response

    def set_context(self, context: dict):
        """
        Actualiza el contexto del asistente.
        Args:
            context (dict): Nuevo contexto.
        """
        self.context = context or ''
