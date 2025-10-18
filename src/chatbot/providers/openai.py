"""
Proveedor de asistente para modelos OpenAI.
Implementa la interfaz AssistantInterface para interactuar con OpenAI.
"""

from .base import AssistantInterface
from src.core.config.settings import settings

from langchain_openai import ChatOpenAI


class OpenAIAssistant(AssistantInterface):
    """
    Asistente basado en modelos OpenAI.
    """

    def __init__(self, model_name: str, temperature: float = 0.7, top_k: int = 40):
        print(
            f"Instanciando OpenAIAssistant con model={model_name}, temp={temperature}, top_k={top_k}"
        )
        self.model_name = model_name
        self.api_key = settings.OPENAI_API_KEY
        self.temperature = temperature
        self.top_k = top_k
        self.context = {}
        self.llm = ChatOpenAI(
            model=model_name, api_key=api_key, temperature=temperature, top_k=top_k
        )

    def generate_response(self, prompt: str, context: dict = None) -> str:
        """
        Llama a la API de OpenAI usando langchain_openai.ChatOpenAI y retorna la respuesta.
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
        response = self.llm.invoke(messages)
        return response.content

    def set_context(self, context: dict):
        """
        Actualiza el contexto del asistente.
        Args:
            context (dict): Nuevo contexto.
        """
        self.context = context or {}
