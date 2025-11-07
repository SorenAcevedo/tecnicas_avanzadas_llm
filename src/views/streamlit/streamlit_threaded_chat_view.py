"""
Vista de Streamlit para el chatbot conversacional.
Interfaz minimalista tipo chat que utiliza el ChatbotController.
"""

import streamlit as st
from src.controllers.chatbot_controller import ChatbotController
from src.config.prompts import PROMPTS
from src.config.settings import settings
from src.tools import get_tools
from src.memory.short_term_memory import generate_thread_id


def initialize_controller():
    """
    Inicializa el controlador del chatbot una sola vez por sesión.
    """
    if "controller" not in st.session_state:
        # Obtener herramientas configuradas
        tools = get_tools()

        st.session_state.controller = ChatbotController(
            model_name="google_genai:gemini-2.5-flash",
            tools=tools,
            temperature=0.1,
            max_tokens=1000,
            system_prompt=PROMPTS["colgate_palmolive_system"],
        )

    return st.session_state.controller


def initialize_chat_history():
    """
    Inicializa el historial de mensajes en el estado de la sesión.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_chat_history(messages: list):
    """
    Muestra el historial de mensajes en la interfaz.
    """
    for message in messages:
        role = message["role"]
        content = message["content"]

        with st.chat_message(role):
            st.markdown(content)


def handle_user_input(controller: ChatbotController, messages: list, thread_id: str):
    """
    Maneja la entrada del usuario y genera la respuesta del asistente.

    Args:
        controller: Instancia del ChatbotController.
        messages: Lista de mensajes del thread activo.
        thread_id: ID del thread activo.
    """
    if prompt := st.chat_input("Escribe tu mensaje..."):
        if st.session_state.new_chat:
            # Crear nuevo thread con ID único
            new_thread_id = generate_thread_id()
            new_thread_name = prompt[:30]  # Truncate to 30 chars
            
            # Guardar thread con su ID y el primer mensaje pendiente
            st.session_state.threads[new_thread_id] = {
                "name": new_thread_name,
                "messages": []
            }
            st.session_state.active_thread = new_thread_id
            st.session_state.new_chat = False
            st.session_state.pending_message = prompt  # Guardar el mensaje para procesarlo después del rerun
            
            # Actualizar el thread_id del controlador
            if "controller" in st.session_state:
                st.session_state.controller.update_thread_id(new_thread_id)
            
            st.rerun()
        
        # Agregar mensaje del usuario al historial
        user_message = {"role": "user", "content": prompt}
        messages.append(user_message)

        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta del asistente
        with st.spinner("Pensando..."):
            try:
                # Convertir mensajes al formato de LangChain
                langchain_messages = [
                    {"role": msg["role"], "content": msg["content"]} for msg in messages
                ]

                # Invocar el controlador
                assistant_content = controller.send_message(langchain_messages)

                # Mostrar respuesta
                st.markdown(assistant_content)

                # Agregar respuesta al historial
                messages.append({"role": "assistant", "content": assistant_content})

            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}"
                st.error(error_msg)
                messages.append({"role": "assistant", "content": error_msg})


def render_model_config_sidebar(controller: ChatbotController):
    """
    Renderiza la barra lateral con información y controles.

    Args:
        controller: Instancia del ChatbotController.
    """
    with st.sidebar:
        st.title("Configuración")

        st.markdown("---")
        st.markdown("### Parámetros del Modelo")

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=controller.model.temperature,
            step=0.1,
            help="Controla la aleatoriedad de las respuestas. Valores más altos = más creatividad.",
        )

        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=controller.model.max_tokens,
            step=100,
            help="Número máximo de tokens en la respuesta.",
        )

        if st.button("Aplicar Cambios"):
            try:
                controller.update_model_config(
                    temperature=temperature, max_tokens=max_tokens
                )
                st.success("Configuración actualizada")
            except ValueError as e:
                st.error(f"Error: {str(e)}")

        st.markdown("---")
        st.markdown("### Estado de la Sesión")
        if st.session_state.active_thread:
            thread_data = st.session_state.threads.get(st.session_state.active_thread, {})
            num_messages = len(thread_data.get("messages", []))
            st.markdown(f"**Mensajes:** {num_messages}")
        st.markdown(f"**Thread ID:** `{controller.thread_id[:8]}...`")

        st.markdown("---")

        if st.session_state.active_thread and st.button(
            "🗑️ Limpiar Hilo Actual"
        ):
            st.session_state.threads[st.session_state.active_thread]["messages"] = []
            st.rerun()

        st.markdown("---")
        st.markdown("### Información")
        st.markdown(
            """
        **Asistente de Colgate Palmolive**
        
        Este chatbot puede ayudarte con:
        - Información de productos
        - Horarios y sedes
        - Historia de la empresa
        - Datos de contacto
        """
        )


def initialize_threading_state():
    """
    Inicializa el estado de la sesión para la gestión de hilos.
    """
    if "threads" not in st.session_state:
        st.session_state.threads = {}
    if "active_thread" not in st.session_state:
        st.session_state.active_thread = None
    if "new_chat" not in st.session_state:
        st.session_state.new_chat = True


def render_thread_sidebar():
    """
    Renderiza la interfaz de gestión de hilos en la barra lateral.
    """
    st.sidebar.title("Conversaciones")

    if st.sidebar.button("➕ Nueva Conversación"):
        st.session_state.new_chat = True
        st.session_state.active_thread = None
        st.rerun()

    st.sidebar.markdown("---")

    # Botones para cada hilo
    for thread_id, thread_data in list(st.session_state.threads.items()):
        col1, col2 = st.sidebar.columns([5, 1])

        with col1:
            # Mostrar el nombre del thread y su ID (primeros 8 caracteres)
            thread_name = thread_data.get("name", "Conversación")
            display_name = f"{thread_name} ({thread_id[:8]}...)"
            
            if st.button(
                display_name,
                key=f"thread_button_{thread_id}",
            ):
                st.session_state.active_thread = thread_id
                st.session_state.new_chat = False
                # Actualizar el thread_id del controlador
                if "controller" in st.session_state:
                    st.session_state.controller.update_thread_id(thread_id)
                st.rerun()

        with col2:
            # Botón de eliminar con icono
            if st.button(
                "🗑️",
                key=f"delete_button_{thread_id}",
                help="Eliminar"
            ):
                del st.session_state.threads[thread_id]
                if st.session_state.active_thread == thread_id:
                    st.session_state.active_thread = None
                    st.session_state.new_chat = True
                st.rerun()


def main():
    """
    Función principal de la aplicación Streamlit.
    """
    # Configuración de la página
    st.set_page_config(
        page_title="Chatbot Colgate Palmolive",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # CSS personalizado para el sidebar
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        [data-testid="stSidebar"] button {
            white-space: normal;
            word-wrap: break-word;
        }
        </style>
    """, unsafe_allow_html=True)

    # Título principal
    st.title("💬 Asistente Virtual Colgate Palmolive")
    st.markdown(
        "Pregúntame sobre productos, horarios, información de la empresa y más."
    )
    st.markdown("---")

    # Inicializar componentes
    initialize_threading_state()  # Nueva función para hilos

    if st.session_state.active_thread is None:
        active_thread_messages = []
        active_thread_id = None
    else:
        active_thread_data = st.session_state.threads[st.session_state.active_thread]
        active_thread_messages = active_thread_data.get("messages", [])
        active_thread_id = st.session_state.active_thread

    # Inicializar controlador una sola vez por sesión
    controller = initialize_controller()
    
    # Actualizar el thread_id si hay un thread activo
    if active_thread_id:
        controller.update_thread_id(active_thread_id)

    # Renderizar barra lateral
    with st.sidebar:
        render_thread_sidebar()  # Nueva función para la gestión de hilos
        render_model_config_sidebar(controller)  # Función renombrada

    # Mostrar historial de chat del hilo activo
    display_chat_history(active_thread_messages)
    
    # Procesar mensaje pendiente si existe (después de crear un nuevo thread)
    if "pending_message" in st.session_state and st.session_state.pending_message:
        prompt = st.session_state.pending_message
        st.session_state.pending_message = None  # Limpiar el mensaje pendiente
        
        # Agregar mensaje del usuario al historial
        user_message = {"role": "user", "content": prompt}
        active_thread_messages.append(user_message)
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta del asistente
        with st.spinner("Pensando..."):
            try:
                # Convertir mensajes al formato de LangChain
                langchain_messages = [
                    {"role": msg["role"], "content": msg["content"]} for msg in active_thread_messages
                ]
                
                # Invocar el controlador
                assistant_content = controller.send_message(langchain_messages)
                
                # Mostrar respuesta
                with st.chat_message("assistant"):
                    st.markdown(assistant_content)
                
                # Agregar respuesta al historial
                active_thread_messages.append({"role": "assistant", "content": assistant_content})
                
            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}"
                with st.chat_message("assistant"):
                    st.error(error_msg)
                active_thread_messages.append({"role": "assistant", "content": error_msg})

    # Manejar entrada del usuario para el hilo activo
    handle_user_input(controller, active_thread_messages, active_thread_id)


if __name__ == "__main__":
    main()
