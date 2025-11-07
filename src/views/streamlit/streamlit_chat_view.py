"""
Vista de Streamlit para el chatbot conversacional.
Interfaz minimalista tipo chat que utiliza el ChatbotController.
"""

import streamlit as st
from src.controllers.chatbot_controller import ChatbotController
from src.config.prompts import PROMPTS
from src.config.settings import settings
from src.config.tools import get_tools
from src.retrieval.vector_store import preload_vector_store


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


def display_chat_history():
    """
    Muestra el historial de mensajes en la interfaz.
    """
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        with st.chat_message(role):
            st.markdown(content)


def handle_user_input(controller: ChatbotController):
    """
    Maneja la entrada del usuario y genera la respuesta del asistente.
    
    Args:
        controller: Instancia del ChatbotController.
    """
    if prompt := st.chat_input("Escribe tu mensaje..."):
        # Agregar mensaje del usuario al historial
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta del asistente
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    # Convertir mensajes al formato de LangChain
                    langchain_messages = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages
                    ]
                    
                    # Invocar el controlador
                    response = controller.send_message(langchain_messages)
                    
                    # Extraer el contenido de la respuesta
                    assistant_content = response.get("messages", [])[-1].content
                    
                    # Mostrar respuesta
                    st.markdown(assistant_content)
                    
                    # Agregar respuesta al historial
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_content
                    })
                    
                except Exception as e:
                    error_msg = f"⚠️ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def render_sidebar(controller: ChatbotController):
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
        st.markdown(f"**Mensajes:** {len(st.session_state.messages)}")
        st.markdown(f"**Thread ID:** `{st.session_state.controller.thread_id[:8]}...`")
        
        st.markdown("---")
        
        if st.button("Limpiar Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("Nueva Conversación", use_container_width=True):
            st.session_state.messages = []
            if "controller" in st.session_state:
                del st.session_state.controller
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
        # Usamos un diccionario para almacenar los hilos y sus mensajes
        st.session_state.threads = {"General": []}
    if "active_thread" not in st.session_state:
        # El hilo activo por defecto será "General"
        st.session_state.active_thread = "General"


def render_thread_sidebar():
    """
    Renderiza la interfaz de gestión de hilos en la barra lateral.
    """
    st.sidebar.title("Conversaciones")

    # Selector de hilos
    thread_names = list(st.session_state.threads.keys())
    st.session_state.active_thread = st.sidebar.selectbox(
        "Selecciona un hilo",
        options=thread_names,
        index=thread_names.index(st.session_state.active_thread)
    )

    # Crear nuevo hilo
    new_thread_name = st.sidebar.text_input("Nombre del nuevo hilo")
    if st.sidebar.button("Crear Hilo"):
        if new_thread_name and new_thread_name not in st.session_state.threads:
            st.session_state.threads[new_thread_name] = []
            st.session_state.active_thread = new_thread_name
            st.rerun()
        else:
            st.sidebar.warning("El nombre del hilo no puede estar vacío o ya existe.")

    # Eliminar hilo actual
    if st.sidebar.button("Eliminar Hilo Actual"):
        if st.session_state.active_thread != "General":
            del st.session_state.threads[st.session_state.active_thread]
            st.session_state.active_thread = "General"
            st.rerun()
        else:
            st.sidebar.warning("No se puede eliminar el hilo 'General'.")


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
    # Pre-cargar la colección vectorial una sola vez por sesión de Streamlit
    if "_kb_preloaded" not in st.session_state:
        try:
            preload_vector_store()  # usa colección y ruta por defecto ya fijadas
        except Exception as e:
            # No bloquea la UI; se mostrará error al consultar si persiste
            st.sidebar.warning(f"Vector store no pre-cargado: {e}")
        st.session_state["_kb_preloaded"] = True
    initialize_chat_history()
    controller = initialize_controller()
    
    # Renderizar barra lateral
    render_sidebar(controller)
    
    # Mostrar historial de chat
    display_chat_history()
    
    # Manejar entrada del usuario
    handle_user_input(controller)
if __name__ == "__main__":
    main()
