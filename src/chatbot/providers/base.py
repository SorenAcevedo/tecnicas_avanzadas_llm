"""
Módulo base para asistentes conversacionales multimodelo.
Define la interfaz abstracta que deben implementar los proveedores (Ollama, Gemini, OpenAI).
"""

from abc import ABC, abstractmethod

class AssistantInterface(ABC):
    """
    Interfaz base para asistentes conversacionales.
    Implementa los métodos que deben tener los proveedores de modelos LLM.
    """
    @abstractmethod
    def generate_response(self, prompt: str, context: dict = None) -> str:
        """
        Genera una respuesta del asistente dado un prompt y contexto opcional.
        Args:
            prompt (str): Pregunta o instrucción del usuario.
            context (dict, opcional): Contexto adicional para la generación.
        Returns:
            str: Respuesta generada por el modelo.
        """
        pass

    @abstractmethod
    def set_context(self, context: dict):
        """
        Actualiza el contexto del asistente.
        Args:
            context (dict): Nuevo contexto para el asistente.
        """
        pass
