"""
Controlador para orquestar la interacción entre la vista y el modelo del chatbot.
Genera thread_id único por sesión y expone método para enviar mensajes.
"""

from src.tools import get_tools
from src.config.prompts import PROMPTS
from src.models.chatbot_model import ChatbotModel
from src.memory.short_term_memory import generate_thread_id

from functools import lru_cache


class ChatbotController:
    def __init__(self, model_name: str, tools, thread_id: str = None, **model_kwargs):
        self.model = ChatbotModel(model_name, tools, **model_kwargs)

    def send_message(self, messages: list, thread_id) -> str:
        """
        Envía mensajes al modelo usando el thread_id de la sesión.

        Args:
            messages (list): Lista de mensajes (dicts) siguiendo el formato de LangChain.

        Returns:
            str: Respuesta generada por el agente.
        """
        return self.model.invoke(messages, thread_id=thread_id)

    def update_model_config(
        self, temperature: float = None, max_tokens: int = None
    ) -> None:
        """
        Actualiza la configuración del modelo sin reiniciar la sesión.

        Args:
            temperature (float, opcional): Nueva temperatura del modelo.
            max_tokens (int, opcional): Nuevo límite de tokens.

        Raises:
            ValueError: Si los parámetros están fuera de los rangos válidos.
        """
        self.model.update_model_config(temperature=temperature, max_tokens=max_tokens)


@lru_cache(maxsize=32)
def get_default_chatbot_controller() -> ChatbotController:
    """
    Proveedor de dependencia para ChatbotController con caching.

    Returns:
        ChatbotController: Instancia del controlador del chatbot.
    """
    return ChatbotController(
        model_name="google_genai:gemini-2.5-flash",
        tools=get_tools(),
        temperature=0.1,
        max_tokens=1000,
        system_prompt=PROMPTS["colgate_palmolive_system"],
    )
