"""
Modelo para la gestión de un agente conversacional basado en LangChain.
Incluye la creación del agente, configuración del modelo, memoria a corto plazo con Postgres y trimming de mensajes.
"""

from typing import Any

from langchain.agents import create_agent, AgentState
from langchain.chat_models import init_chat_model
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime

from src.memory.short_term_memory import (
    create_checkpointer_context,
    generate_thread_id,
)


class ChatbotModel:
    """
    Clase que encapsula la lógica de creación e invocación de un agente conversacional
    utilizando LangChain, memoria a corto plazo en Postgres y trimming de mensajes.
    """

    def __init__(
        self,
        model_name: str,
        tools: list[Any],
        temperature: float = 0.1,
        max_tokens: int = 1000,
        timeout: int = 30,
        system_prompt: str = None,
    ):
        """
        Inicializa el modelo del chatbot.

        Args:
            model_name (str): Nombre o identificador del modelo (por ejemplo, 'gpt-4o').
            tools (List[Any]): Lista de herramientas para el agente.
            temperature (float): Temperatura del modelo (creatividad).
            max_tokens (int): Máximo de tokens en la respuesta.
            timeout (int): Tiempo máximo de espera para la respuesta.
            system_prompt (str, opcional): Prompt del sistema para el agente.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.model = init_chat_model(
            model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        self.tools = tools
        self.system_prompt = system_prompt
        self._checkpointer_cm = create_checkpointer_context()
        self.checkpointer = self._checkpointer_cm.__enter__()
        self.checkpointer.setup()
        self.agent = self._create_agent()

    @staticmethod
    @before_model
    def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """
        Middleware para trimming: mantiene solo los últimos 4 mensajes relevantes en el historial.
        """
        messages = state["messages"]
        if len(messages) <= 4:
            return None
        first_msg = messages[0]
        recent_messages = messages[-4:]
        new_messages = [first_msg] + recent_messages
        return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *new_messages]}

    def _create_agent(self):
        """
        Crea una instancia del agente LangChain con el modelo, herramientas, memoria y trimming.
        Returns:
            Agent: Instancia del agente LangChain.
        """
        return create_agent(
            self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
            middleware=[self.trim_messages],
            checkpointer=self.checkpointer,
        )

    def update_model_config(
        self, temperature: float = None, max_tokens: int = None
    ) -> None:
        """
        Actualiza la configuración del modelo y recrea el agente con los nuevos parámetros.

        Args:
            temperature (float, opcional): Nueva temperatura del modelo.
                Si no se proporciona, mantiene el valor actual.
            max_tokens (int, opcional): Nuevo límite de tokens.
                Si no se proporciona, mantiene el valor actual.

        Raises:
            ValueError: Si los parámetros están fuera de los rangos válidos.
        """
        if temperature is not None:
            if not 0.0 <= temperature <= 1.0:
                raise ValueError("Temperature must be between 0.0 and 1.0")
            self.temperature = temperature

        if max_tokens is not None:
            if max_tokens <= 0:
                raise ValueError("Max tokens must be greater than 0")
            self.max_tokens = max_tokens

        self.model = init_chat_model(
            self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
        )
        self.agent = self._create_agent()

    def _get_text_from_content(self, content) -> str:
        """
        Extrae texto plano del contenido del mensaje, manejando listas si es necesario.

        Args:
            content: Contenido del mensaje (puede ser str o lista de dicts).

        Returns:
            str: Texto plano extraído del contenido.
        """
        if isinstance(content, list):
            return " ".join(item.get("text", "") for item in content if "text" in item)
        return content

    def invoke(
        self, messages: list, thread_id: str = None, output_keys="messages", **kwargs
    ):
        """
        Invoca el agente con historial de mensajes y un identificador de conversación único.
        Si no se provee thread_id, se genera uno nuevo (uuid4).

        Args:
            messages (list): Lista de mensajes (dicts) siguiendo el formato de LangChain.
            thread_id (str, opcional): Identificador único de la conversación.
            **kwargs: Parámetros adicionales para la invocación.

        Returns:
            dict: Respuesta generada por el agente.
        """
        if thread_id is None:
            thread_id = generate_thread_id()

        config = {"configurable": {"thread_id": thread_id}}

        response = self.agent.invoke(
            {"messages": messages}, config, output_keys=output_keys
        )

        if isinstance(response, dict) and "messages" in response:
            last_message = response["messages"][-1]
            return self._get_text_from_content(last_message.content)

        if isinstance(response, list):
            return self._get_text_from_content(response[-1].content)

        return self._get_text_from_content(response["messages"][-1].content)

    def __del__(self):
        """Cerrar el context manager al destruir el objeto."""
        if hasattr(self, "_checkpointer_cm"):
            self._checkpointer_cm.__exit__(None, None, None)
