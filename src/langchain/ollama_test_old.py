# from langchain_ollama import ChatOllama

# # --- 1. Configurar el modelo Ollama ---
# llm = ChatOllama(
#     model="gpt-oss",
#     validate_model_on_init=True,
#     temperature=0.8,
#     num_predict=256
# )

# # --- 2. Leer el contexto desde un archivo .txt ---
# with open("contexto.txt", "r", encoding="utf-8") as f:
#     context = f.read()

# # --- 3. Definir la pregunta del usuario ---
# question = "¿Cuál es la misión de la empresa según el texto?"

# # --- 4. Armar los mensajes para el modelo ---
# messages = [
#     ("system", "Eres un asistente experto que responde preguntas usando el contexto proporcionado."),
#     ("human", f"Contexto:\n{context}\n\nPregunta: {question}")
# ]

# # --- 5. Invocar el modelo ---
# response = llm.invoke(messages)

# print("🧠 Respuesta generada:\n")
# print(response.content)
import streamlit as st
from langchain_ollama import ChatOllama

# --- CONFIGURACIÓN DE STREAMLIT ---
st.set_page_config(page_title="Asistente con Contexto (Ollama + GPT-OSS)", page_icon="🧩")

st.title("🧠 Asistente IA con Contexto Local (Ollama + GPT-OSS)")
st.write("Haz preguntas basadas en el contenido de tu archivo de texto.")

# --- CARGAR CONTEXTO ---
with open("contexto.txt", "r", encoding="utf-8") as f:
    context = f.read()

# --- CONFIGURAR EL MODELO OLLAMA ---
llm = ChatOllama(
    model="qwen3:1.7b",           # Modelo Ollama
    validate_model_on_init=True,
    temperature=0.7,
    num_predict=512
)

# --- INTERFAZ DE USUARIO ---
question = st.text_input("💬 Escribe tu pregunta:")

if st.button("Preguntar") and question.strip():
    with st.spinner("Pensando... 🧠"):
        messages = [
            ("system", "Eres un asistente útil que responde con precisión usando el contexto proporcionado."),
            ("human", f"Contexto:\n{context}\n\nPregunta: {question}")
        ]

        response = llm.invoke(messages)
        st.success("Respuesta:")
        st.write(response.content)

