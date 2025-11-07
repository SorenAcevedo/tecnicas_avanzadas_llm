"""
Vista de Streamlit para el chatbot conversacional.
Interfaz minimalista tipo chat que utiliza el ChatbotController.
"""

import streamlit as st
from src.controllers.chatbot_controller import ChatbotController
from src.config.prompts import PROMPTS
from src.config.settings import settings
from src.config.tools import get_tools


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


def handle_user_input(controller: ChatbotController, messages: list):
    """
    Maneja la entrada del usuario y genera la respuesta del asistente.
    
    Args:
        controller: Instancia del ChatbotController.
    """
    if prompt := st.chat_input("Escribe tu mensaje..."):
        if st.session_state.new_chat:
            new_thread_name = prompt[:30] # Truncate to 30 chars
            st.session_state.threads[new_thread_name] = []
            st.session_state.active_thread = new_thread_name
            st.session_state.new_chat = False
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
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in messages
                    ]
                    
                    # Invocar el controlador
                    response = controller.send_message(langchain_messages)
                    
                    # Extraer el contenido de la respuesta
                    if isinstance(response, list) and len(response) > 0 and isinstance(response[0], dict):
                        # Respuesta de Gemini
                        if 'text' in response[0]:
                            assistant_content = response[0]['text']
                        else:
                            assistant_content = str(response)
                    else:
                        # Respuesta normal de LangChain
                        assistant_content = response.get("messages", [])[-1].content
                    
                    # Mostrar respuesta
                    st.markdown(assistant_content)
                    
                    # Agregar respuesta al historial
                    messages.append({
                        "role": "assistant",
                        "content": assistant_content
                    })
                    
                except Exception as e:
                    error_msg = f"⚠️ Error: {str(e)}"
                    st.error(error_msg)
                    messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


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
            help="Controla la aleatoriedad de las respuestas. Valores más altos = más creatividad."
        )
        
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=controller.model.max_tokens,
            step=100,
            help="Número máximo de tokens en la respuesta."
        )
        
        if st.button("Aplicar Cambios", use_container_width=True):
            try:
                controller.update_model_config(
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                st.success("Configuración actualizada")
            except ValueError as e:
                st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        st.markdown("### Estado de la Sesión")
        if st.session_state.active_thread:
            st.markdown(f"**Mensajes:** {len(st.session_state.threads[st.session_state.active_thread])}")
        st.markdown(f"**Thread ID:** `{st.session_state.controller.thread_id[:8]}...`")
        
        st.markdown("---")
        
        if st.session_state.active_thread and st.button("Limpiar Hilo Actual", use_container_width=True):
            st.session_state.threads[st.session_state.active_thread] = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Información")
        st.markdown("""
        **Asistente de Colgate Palmolive**
        
        Este chatbot puede ayudarte con:
        - Información de productos
        - Horarios y sedes
        - Historia de la empresa
        - Datos de contacto
        """)


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

    if st.sidebar.button("Nueva Conversación", use_container_width=True):
        st.session_state.new_chat = True
        st.session_state.active_thread = None
        st.rerun()

    st.sidebar.markdown("---")

    # Botones para cada hilo
    for thread_name in list(st.session_state.threads.keys()):
        col1, col2 = st.sidebar.columns([0.8, 0.2])
        
        with col1:
            if st.button(thread_name, key=f"thread_button_{thread_name}", use_container_width=True):
                st.session_state.active_thread = thread_name
                st.session_state.new_chat = False
                st.rerun()

        with col2:
            with st.popover("", use_container_width=True):
                if st.button("Eliminar", key=f"delete_button_{thread_name}", use_container_width=True):
                    del st.session_state.threads[thread_name]
                    if st.session_state.active_thread == thread_name:
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
    
    # Título principal
    st.title("💬 Asistente Virtual Colgate Palmolive")
    st.markdown("Pregúntame sobre productos, horarios, información de la empresa y más.")
    st.markdown("---")
    
    # Inicializar componentes
    initialize_threading_state() # Nueva función para hilos
    
    if st.session_state.active_thread is None:
        active_thread_messages = []
    else:
        active_thread_messages = st.session_state.threads[st.session_state.active_thread]
    
    controller = initialize_controller() # El controlador se inicializa una vez por sesión
    
    # Renderizar barra lateral
    with st.sidebar:
        render_thread_sidebar() # Nueva función para la gestión de hilos
        render_model_config_sidebar(controller) # Función renombrada
    
    # Mostrar historial de chat del hilo activo
    display_chat_history(active_thread_messages)
    
    # Manejar entrada del usuario para el hilo activo
    handle_user_input(controller, active_thread_messages)


if __name__ == "__main__":
    main()
