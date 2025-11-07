"""
Controlador para orquestar la interacción entre la vista y el modelo del chatbot.
Genera thread_id único por sesión y expone método para enviar mensajes.
"""

from src.models.chatbot_model import ChatbotModel
from src.memory.short_term_memory import generate_thread_id


class ChatbotController:
    def __init__(self, model_name: str, tools, **model_kwargs):
        self.model = ChatbotModel(model_name, tools, **model_kwargs)
        self.thread_id = generate_thread_id()

    def send_message(self, messages: list) -> dict:
        """
        Envía mensajes al modelo usando el thread_id de la sesión.
        
        Args:
            messages (list): Lista de mensajes (dicts) siguiendo el formato de LangChain.
        
        Returns:
            dict: Respuesta generada por el agente.
        """
        response = self.model.invoke(messages, thread_id=self.thread_id)
        
        # Si la respuesta es una lista y contiene el formato de Gemini
        if isinstance(response, list) and len(response) > 0 and isinstance(response[0], dict):
            if 'text' in response[0]:
                return {"messages": [{"content": response[0]['text']}]}
        
        # Si es una respuesta normal de LangChain
        return response
    
    def update_model_config(self, temperature: float = None, max_tokens: int = None) -> None:
        """
        Actualiza la configuración del modelo sin reiniciar la sesión.
        
        Args:
            temperature (float, opcional): Nueva temperatura del modelo.
            max_tokens (int, opcional): Nuevo límite de tokens.
        
        Raises:
            ValueError: Si los parámetros están fuera de los rangos válidos.
        """
        self.model.update_model_config(temperature=temperature, max_tokens=max_tokens)
