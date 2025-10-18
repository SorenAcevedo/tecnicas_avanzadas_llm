"""
Proveedor de asistente para modelos Gemini.
Implementa la interfaz AssistantInterface para interactuar con Gemini.
"""

from src.core.prompts import PROMPTS
from src.core.config.env_settings import settings
from src.core.logging.logger import get_logger
from langchain_google_genai import ChatGoogleGenerativeAI
from .base import AssistantInterface


class GeminiAssistant(AssistantInterface):
    """
    Asistente basado en modelos Gemini.
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        top_k: int = 40,
    ):
        self.api_key = settings.gemini_api_key
        self.logger = get_logger(__name__)
        self.logger.info(
            f"Instanciando GeminiAssistant con model={model_name}, temp={temperature}, top_k={top_k}"
        )
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.top_k = top_k
        self.context = PROMPTS["colgate_palmolive_system"]
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, api_key=api_key, temperature=temperature, top_k=top_k
        )

    def generate_response(self, prompt: str, context: dict = None) -> str:
        """
        Llama a la API de Gemini usando langchain_google_genai.ChatGoogleGenerativeAI y retorna la respuesta.
        Args:
            prompt (str): Pregunta del usuario.
            context (dict, opcional): Contexto adicional.
        Returns:
            str: Respuesta generada.
        """
        messages = []
        if context:
            messages.append(("system", context))
        messages.append(("human", str(prompt)))
        self.logger.debug(f"Mensajes enviados a Gemini ({self.model_name}): {messages}")
        response = self.llm.invoke(messages)
        self.logger.info(
            f"Respuesta generada por Gemini ({self.model_name}): {response}"
        )
        return response.content

    def set_context(self, context: dict):
        """
        Actualiza el contexto del asistente.
        Args:
            context (dict): Nuevo contexto.
        """
        self.context = context or {}
