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
    "Compañía": os.path.join(PROCESSED_DIR, "company_context.txt"),
}

context_options = list(CONTEXT_FILES.keys()) + ["Usar todo"]
brand = st.sidebar.selectbox("Selecciona contexto", context_options, index=len(context_options)-1)



st.set_page_config(layout="wide")

@st.cache_data(show_spinner=False)
def load_context(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

if brand == "Usar todo":
    context_text = "\n\n".join([load_context(path) for path in CONTEXT_FILES.values()])
else:
    context_text = load_context(CONTEXT_FILES[brand])

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
        model_name=selected_model, temperature=temperature, top_k=top_k
    )

st.title("Asistente Colgate Palmolive")

if "messages" not in st.session_state:
    st.session_state.messages = []
if 'history' not in st.session_state:
    st.session_state.history = []


# Tabs para chat, histórico y testing QA
tab1, tab2, tab3 = st.tabs(["Chat", "Histórico de Peticiones", "Testing QA"])

with tab1:
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
    import random
    ayuda_preguntas = [
        "¿Qué crema dental de Colgate tiene coco o extracto natural?",
        "¿Cuál es la mejor crema dental Colgate para la sensibilidad dental?",
        "¿Qué producto Colgate me ayuda a blanquear los dientes rápido?",
        "¿Qué cremas dentales de Colgate están disponibles en Éxito?",
        "¿Qué crema Colgate es buena para encías inflamadas?",
        "¿Palmolive tiene jabón o gel de baño con aroma a coco?",
        "¿Qué productos de Palmolive sirven para lavar platos?",
        "¿Dónde puedo comprar Colgate Sensitive Pro Alivio en Colombia?",
        "¿Qué crema dental Colgate es para niños pequeños?",
        "¿Qué productos Colgate o Palmolive son ecológicos o sostenibles?"
    ]
    if 'ayuda_pregunta' not in st.session_state:
        st.session_state.ayuda_pregunta = ""
    if st.button("¿Necesitas inspiración? Muestra una pregunta de ejemplo"):
        st.session_state.ayuda_pregunta = random.choice(ayuda_preguntas)
    if st.session_state.ayuda_pregunta:
        st.info(f"Ejemplo: {st.session_state.ayuda_pregunta}")

    with st.form("chat_form"):
        user_input = st.text_area(
            "Pregunta:", st.session_state.ayuda_pregunta, placeholder="Haz tu pregunta y presiona Enviar"
        )
        submitted = st.form_submit_button("Enviar")

        if submitted and user_input.strip():
            st.session_state.messages.append(("user", user_input, None))
            st.session_state.ayuda_pregunta = ""
            with st.spinner("Pensando..."):
                start = time.time()
                contexto = context_text
                system_prompt = PROMPTS.get("colgate_palmolive_system", "")
                system_prompt = str(system_prompt)
                response = assistant.generate_response(user_input, context=system_prompt + "\n" + contexto)
                end = time.time()
                duration = end - start
                st.session_state.messages.append(("bot", getattr(response, "content", response), duration))
                # Registro histórico usando response del llm.invoke si tiene atributos
                # Extraer tokens desde usage_metadata si existe
                usage_metadata = getattr(response, "usage_metadata", None)
                if usage_metadata:
                    tokens_in = usage_metadata.get("input_tokens", len(user_input.split()))
                    tokens_out = usage_metadata.get("output_tokens", len(str(getattr(response, "content", response)).split()))
                else:
                    tokens_in = getattr(response, "usage", {}).get("prompt_tokens", len(user_input.split())) if hasattr(response, "usage") else len(user_input.split())
                    tokens_out = getattr(response, "usage", {}).get("completion_tokens", len(str(getattr(response, "content", response)).split())) if hasattr(response, "usage") else len(str(getattr(response, "content", response)).split())
                st.session_state.history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "modelo": f"{provider}:{selected_model}",
                    "temperatura": temperature,
                    "top_k": top_k,
                    "user_msg": user_input,
                    "bot_msg": getattr(response, "content", response),
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                })
            st.rerun()

with tab2:
    st.subheader("Histórico de Peticiones")
    import pandas as pd
    if st.session_state.history and len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, width='stretch')
    else:
        st.info("Aún no hay historial de peticiones.")

with tab3:
    st.subheader("Testing QA")
    st.info("Automatiza pruebas sobre todo el contexto. Se ejecutarán preguntas del archivo externo y se mostrarán las respuestas.")

    import pandas as pd
    qa_path = os.path.join("data", "qa", "qa_colgate_palmolive.csv")
    qa_df = pd.read_csv(qa_path)

    import random
    qa_levels = {
        "Ligera (5 preguntas)": 5,
        "Mediana (10 preguntas)": 10,
        "Robusta (20 preguntas)": 20,
        "Completa (todas)": len(qa_df)
    }
    qa_level = st.selectbox("Nivel de QA", list(qa_levels.keys()), index=0)
    n_questions = qa_levels[qa_level]

    if st.button("▶️ Ejecutar pruebas automáticas QA"):
        st.info(f"Ejecutando {n_questions} preguntas aleatorias sobre todo el contexto, por favor espera...")
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        qa_results = []
        qa_sample = qa_df.sample(n=n_questions, random_state=42) if n_questions < len(qa_df) else qa_df
        qa_sample = qa_sample.reset_index(drop=True)
        for i, row in qa_sample.iterrows():
            q = row["Pregunta"]
            expected = row["Respuesta esperada"]
            status_placeholder.markdown(f"🔹 <b>Pregunta {i+1}/{len(qa_sample)}:</b> {q}", unsafe_allow_html=True)
            contexto = "\n\n".join([load_context(path) for path in CONTEXT_FILES.values()])
            with st.spinner(f"Procesando pregunta {i+1}..."):
                start = time.time()
                if provider == 'ollama':
                    system_prompt = PROMPTS.get("colgate_palmolive_system", "")
                    if not isinstance(system_prompt, str):
                        system_prompt = str(system_prompt)
                    if not isinstance(contexto, str):
                        contexto = str(contexto)
                    response = assistant.generate_response(q, context=system_prompt + "\n" + contexto)
                elif provider == 'openai' or provider == 'gemini':
                    if not isinstance(contexto, str):
                        contexto = str(contexto)
                    response = assistant.generate_response(q, context=contexto)
                end = time.time()
                duration = end - start
                answer = getattr(response, "content", response)
                qa_results.append({
                    "Pregunta": q,
                    "Respuesta esperada": expected,
                    "Respuesta obtenida": answer,
                    "Tiempo": f"{duration:.2f} seg" if duration < 60 else f"{int(duration // 60)} min {int(duration % 60)} seg"
                })
            progress_bar.progress((i+1) / len(qa_sample))
        status_placeholder.empty()
        st.success("Pruebas automáticas completadas.")
        st.markdown("---")
        qa_results_df = pd.DataFrame(qa_results)
        st.dataframe(qa_results_df, width='stretch', hide_index=True)
