import streamlit as st
from langchain_ollama import ChatOllama
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="🧩 Asistente IA (Ollama + GPT-OSS)",
    page_icon="🧠",
    layout="wide",
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
<style>
    body {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .main {
        background-color: #161a23;
        border-radius: 15px;
        padding: 20px;
    }
    .stButton > button {
        border-radius: 12px;
        background-color: #0078ff;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #005dcc;
    }
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        display: inline-block;
    }
    .user-bubble {
        background-color: #1f6feb;
        color: white;
        text-align: right;
        margin-left: auto;
    }
    .bot-bubble {
        background-color: #2d333b;
        color: #e6edf3;
        text-align: left;
        margin-right: auto;
    }
    .time-info {
        font-size: 0.8em;
        color: #a0a0a0;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- CARGAR CONTEXTO ---
with open("contexto.txt", "r", encoding="utf-8") as f:
    context = f.read()

# --- CONFIGURAR EL MODELO ---
llm = ChatOllama(
    model="qwen3:1.7b",  # puedes cambiar a "qwen3:1.7b"
    validate_model_on_init=True,
    temperature=0.7,
    num_predict=2048  
)

# --- ESTADO DE SESIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TÍTULO ---
st.title("🧠 Asistente IA con Contexto Local")
st.caption("Interfaz interactiva impulsada por **Ollama + GPT-OSS**")

# --- CAJA DE CHAT ---
with st.container():
    for msg in st.session_state.messages:
        role, content, duration = msg
        bubble_class = "user-bubble" if role == "user" else "bot-bubble"
        st.markdown(f"<div class='chat-bubble {bubble_class}'>{content}</div>", unsafe_allow_html=True)
        if role == "bot" and duration is not None:
            if duration < 60:
                time_text = f"⏱️ Tiempo de respuesta: {duration:.2f} segundos"
            else:
                mins = int(duration // 60)
                secs = int(duration % 60)
                time_text = f"⏱️ Tiempo de respuesta: {mins} min {secs} segundos"
            st.markdown(f"<span class='time-info'>{time_text}</span>", unsafe_allow_html=True)

# --- ENTRADA DEL USUARIO ---
user_question = st.text_input("💬 Escribe tu pregunta aquí:")

col1, col2 = st.columns([1, 1])
with col1:
    ask = st.button("🚀 Enviar pregunta")
with col2:
    clear = st.button("🧹 Limpiar chat")

if clear:
    st.session_state.messages = []
    st.rerun()

if ask and user_question.strip():
    st.session_state.messages.append(("user", user_question, None))
    with st.spinner("Pensando... 🤔"):
        start = time.time()
        messages = [
            ("system", "Eres un asistente útil que responde con precisión usando el contexto proporcionado."),
            ("human", f"Contexto:\n{context}\n\nPregunta: {user_question}")
        ]
        response = llm.invoke(messages)
        end = time.time()
        duration = end - start
        st.session_state.messages.append(("bot", response.content, duration))
        st.rerun()

# --- PREGUNTAS PREDEFINIDAS ---
st.subheader("🎯 Preguntas predefinidas")

preset_questions = [
    "¿Cuál es el propósito principal del documento?",
    "Resume el contenido en tres frases.",
    "¿Qué entidades o personas se mencionan más?",
    "¿Qué problema intenta resolver el texto?",
    "¿Qué soluciones propone?",
    "¿Cuáles son los principales desafíos?",
    "Explica los puntos clave en formato de lista.",
    "Dame un resumen técnico.",
    "Dame un resumen ejecutivo.",
    "¿Qué datos o métricas relevantes aparecen?",
    "¿Qué recomendaciones se pueden derivar?",
    "¿Cuál es el tono general del texto?",
    "¿Qué supuestos se hacen en el documento?",
    "¿Qué partes requieren validación adicional?",
    "Dame una cita textual clave.",
    "¿Hay alguna contradicción o ambigüedad?",
    "¿Cómo se podría aplicar este conocimiento?",
    "Dame un resumen para principiantes.",
    "Dame un resumen para expertos.",
    "Propón una pregunta adicional relevante."
]

colA, colB = st.columns([2, 1])

with colA:
    for i, q in enumerate(preset_questions, start=1):
        if st.button(f"❓ {i}. {q}"):
            st.session_state.messages.append(("user", q, None))
            with st.spinner(f"Analizando pregunta {i}..."):
                start = time.time()
                messages = [
                    ("system", "Eres un asistente útil que responde con precisión usando el contexto proporcionado."),
                    ("human", f"Contexto:\n{context}\n\nPregunta: {q}")
                ]
                response = llm.invoke(messages)
                end = time.time()
                duration = end - start
                st.session_state.messages.append(("bot", response.content, duration))
                st.rerun()

with colB:
    if st.button("▶️ Ejecutar todas secuencialmente"):
        st.info("🚀 Ejecutando preguntas automáticamente, por favor espera...")
        progress_bar = st.progress(0)
        status_placeholder = st.empty()

        # ✅ Contenedor persistente donde se irán acumulando las respuestas
        chat_container = st.container()

        for i, q in enumerate(preset_questions, start=1):
            status_placeholder.markdown(f"🔹 **Pregunta {i}/{len(preset_questions)}:** {q}")

            # Agregar la pregunta al historial y mostrarla
            st.session_state.messages.append(("user", q, None))
            with chat_container:
                st.markdown(f"<div class='chat-bubble user-bubble'>{q}</div>", unsafe_allow_html=True)

            # Llamar al modelo
            with st.spinner(f"Procesando pregunta {i}..."):
                start = time.time()
                messages = [
                    ("system", "Eres un asistente útil que responde con precisión usando el contexto proporcionado."),
                    ("human", f"Contexto:\n{context}\n\nPregunta: {q}")
                ]
                response = llm.invoke(messages)
                end = time.time()
                duration = end - start

            # Agregar respuesta y mostrarla debajo
            st.session_state.messages.append(("bot", response.content, duration))
            with chat_container:
                st.markdown(f"<div class='chat-bubble bot-bubble'>{response.content}</div>", unsafe_allow_html=True)

                if duration < 60:
                    time_text = f"⏱️ Tiempo de respuesta: {duration:.2f} segundos"
                else:
                    mins = int(duration // 60)
                    secs = int(duration % 60)
                    time_text = f"⏱️ Tiempo de respuesta: {mins} min {secs} segundos"

                st.markdown(f"<span class='time-info'>{time_text}</span>", unsafe_allow_html=True)

            # Actualizar progreso
            progress_bar.progress(i / len(preset_questions))
            time.sleep(0.5)

        status_placeholder.empty()
        st.success("🎉 Ejecución de todas las preguntas completada.")
