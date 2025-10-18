import streamlit as st
import sys
import os
import time

from src.core.prompts import PROMPTS
from src.core.config.model_loader import load_model_config
from src.chatbot.providers.ollama import OllamaAssistant
from src.chatbot.providers.openai import OpenAIAssistant
from src.chatbot.providers.gemini import GeminiAssistant

# Cargar configuración de modelos
model_config = load_model_config()

# Genera opciones tipo 'proveedor:modelo'
model_options = []
for provider, data in model_config.items():
    for model in data["models"]:
        model_options.append(f"{provider}:{model}")

selected_option = st.sidebar.selectbox("Selecciona proveedor y modelo", model_options)

provider, selected_model = selected_option.split(":", 1)

# Selector de contexto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
CONTEXT_FILES = {
    "Colgate": os.path.join(PROCESSED_DIR, "context_colgate.txt"),
    "Palmolive": os.path.join(PROCESSED_DIR, "context_palmolive.txt"),
    "YouTube": os.path.join(PROCESSED_DIR, "context_youtube.txt"),
}

brand = st.sidebar.selectbox("Selecciona contexto", list(CONTEXT_FILES.keys()))


@st.cache_data(show_spinner=False)
def load_context(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        blocks = f.read().split("---")
        return [b.strip() for b in blocks if b.strip()]


context_blocks = load_context(CONTEXT_FILES[brand])

selected_blocks = st.sidebar.multiselect(
    "Selecciona productos para el contexto",
    options=range(len(context_blocks)),
    format_func=lambda i: context_blocks[i].split("\n")[0][:60],
)

# Sliders para parámetros del modelo
temperature = st.sidebar.slider(
    "Temperatura", min_value=0.0, max_value=2.0, value=0.7, step=0.05
)
top_k = st.sidebar.slider("Top K", min_value=1, max_value=100, value=40, step=1)

# Instancia el asistente según el proveedor y modelo
if provider == "ollama":
    assistant = OllamaAssistant(
        model_name=selected_model, temperature=temperature, top_k=top_k
    )
elif provider == "openai":
    assistant = OpenAIAssistant(
        model_name=selected_model,
        temperature=temperature,
        top_k=top_k,
    )
else:
    assistant = GeminiAssistant(
        model_name=selected_model, api_key="xxx", temperature=temperature, top_k=top_k
    )

st.title("Asistente Colgate Palmolive")

if "messages" not in st.session_state:
    st.session_state.messages = []
if 'history' not in st.session_state:
    st.session_state.history = []

with st.container():
    for msg in st.session_state.messages:
        role, content, duration = (
            msg if len(msg) == 3 else (msg["role"], msg["content"], None)
        )
        bubble_class = "user-bubble" if role == "user" else "bot-bubble"
        st.markdown(
            f"<div style='padding:10px 15px;border-radius:10px;margin:5px 0;display:inline-block;background:{'#1f6feb' if role=='user' else '#2d333b'};color:{'white' if role=='user' else '#e6edf3'};'>{content}</div>",
            unsafe_allow_html=True,
        )
        if role == "bot" and duration is not None:
            if duration < 60:
                time_text = f"⏱️ Tiempo de respuesta: {duration:.2f} segundos"
            else:
                mins = int(duration // 60)
                secs = int(duration % 60)
                time_text = f"⏱️ Tiempo de respuesta: {mins} min {secs} segundos"
            st.markdown(
                f"<span style='font-size:0.8em;color:#a0a0a0;margin-left:8px;'>{time_text}</span>",
                unsafe_allow_html=True,
            )

with st.form("chat_form"):
    user_input = st.text_area(
        "Pregunta:", "", placeholder="Haz tu pregunta y presiona Enviar"
    )
    submitted = st.form_submit_button("Enviar")

    if submitted and user_input.strip():
        st.session_state.messages.append(("user", user_input, None))
        with st.spinner("Pensando..."):
            start = time.time()
            contexto = '\n'.join([context_blocks[i] for i in selected_blocks]) if selected_blocks else ''
            if provider == 'ollama':
                system_prompt = PROMPTS.get("colgate_palmolive_system", "")
                response = assistant.generate_response(user_input, context=system_prompt + "\n" + contexto)
            elif provider == 'openai' or provider == 'gemini':
                response = assistant.generate_response(user_input, context=contexto)
            end = time.time()
            duration = end - start
            st.session_state.messages.append(("bot", response, duration))
            # Simulación de tokens (puedes reemplazar por el conteo real si lo tienes)
            tokens = len(user_input.split()) + len(str(response).split())
            st.session_state.history.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "modelo": f"{provider}:{selected_model}",
                "temperatura": temperature,
                "top_k": top_k,
                "user_msg": user_input,
                "bot_msg": response,
                "tokens": tokens
            })
        st.rerun()



# Tabs para chat, histórico y testing QA
tab1, tab2, tab3 = st.tabs(["Chat", "Histórico de Peticiones", "Testing QA"])

with tab1:
    st.title("Asistente Colgate Palmolive")
    with st.container():
        for msg in st.session_state.messages:
            role, content, duration = (
                msg if len(msg) == 3 else (msg["role"], msg["content"], None)
            )
            bubble_class = "user-bubble" if role == "user" else "bot-bubble"
            st.markdown(
                f"<div style='padding:10px 15px;border-radius:10px;margin:5px 0;display:inline-block;background:{{'#1f6feb' if role=='user' else '#2d333b'}};color:{{'white' if role=='user' else '#e6edf3'}};'>{{content}}</div>",
                unsafe_allow_html=True,
            )
            if role == "bot" and duration is not None:
                if duration < 60:
                    time_text = f"⏱️ Tiempo de respuesta: {{duration:.2f}} segundos"
                else:
                    mins = int(duration // 60)
                    secs = int(duration % 60)
                    time_text = f"⏱️ Tiempo de respuesta: {{mins}} min {{secs}} segundos"
                st.markdown(
                    f"<span style='font-size:0.8em;color:#a0a0a0;margin-left:8px;'>{{time_text}}</span>",
                    unsafe_allow_html=True,
                )
    with st.form("chat_form"):
        user_input = st.text_area(
            "Pregunta:", "", placeholder="Haz tu pregunta y presiona Enviar"
        )
        submitted = st.form_submit_button("Enviar")

        if submitted and user_input.strip():
            st.session_state.messages.append(("user", user_input, None))
            with st.spinner("Pensando..."):
                start = time.time()
                contexto = '\n'.join([context_blocks[i] for i in selected_blocks]) if selected_blocks else ''
                if provider == 'ollama':
                    system_prompt = PROMPTS.get("colgate_palmolive_system", "")
                    response = assistant.generate_response(user_input, context=system_prompt + "\n" + contexto)
                elif provider == 'openai' or provider == 'gemini':
                    response = assistant.generate_response(user_input, context=contexto)
                end = time.time()
                duration = end - start
                st.session_state.messages.append(("bot", response, duration))
                # Simulación de tokens (puedes reemplazar por el conteo real si lo tienes)
                tokens = len(user_input.split()) + len(str(response).split())
                st.session_state.history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "modelo": f"{provider}:{selected_model}",
                    "temperatura": temperature,
                    "top_k": top_k,
                    "user_msg": user_input,
                    "bot_msg": response,
                    "tokens": tokens
                })
            st.rerun()
    st.markdown("---")
    st.subheader('Contexto actual')
    if selected_blocks:
        context_text = '\n---\n'.join([context_blocks[i] for i in selected_blocks])
        st.code(context_text, language=None)
    else:
        st.info('Selecciona al menos un producto para el contexto.')

with tab2:
    st.subheader("Histórico de Peticiones")
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            st.markdown(f"""
**Fecha:** {item['timestamp']}  
**Modelo:** {item['modelo']}  
**Temperatura:** {item['temperatura']}  
**Top K:** {item['top_k']}  
**Tokens (simulado):** {item['tokens']}  
**Usuario:** {item['user_msg']}  
**Asistente:** {item['bot_msg']}  
---
""")
    else:
        st.info("Aún no hay historial de peticiones.")

with tab3:
    st.subheader("Testing QA")
    st.info("Aquí podrás agregar pruebas o validaciones de calidad para el asistente.")
