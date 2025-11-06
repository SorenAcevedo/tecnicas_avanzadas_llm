# Sistema de Chatbot Conversacional - Colgate Palmolive

Sistema de chatbot inteligente basado en LangChain con arquitectura por capas, memoria persistente en PostgreSQL y capacidades RAG (Retrieval-Augmented Generation) para consultas sobre productos y servicios de Colgate Palmolive.

## 👥 Integrantes del grupo

- Juan Jose Bonilla - 22502052
- Yan Carlos Cuaran Imbacuan - 22502591
- Nicolas Lozano Mazuera - 22500565
- Soren Acevedo - 22500566

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Flujo de Datos](#flujo-de-datos)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Comandos Make](#comandos-make)
- [ETL Pipeline](#etl-pipeline)
- [Tecnologías](#tecnologías)

## ✨ Características

- **Chatbot conversacional** con memoria de corto plazo persistente
- **Arquitectura por capas** (Layered Architecture + Clean Architecture)
- **RAG** con base de datos vectorial para búsqueda semántica (en desarrollo)
- **Persistencia** de conversaciones en PostgreSQL
- **Trimming automático** de mensajes para optimizar contexto
- **Configuración dinámica** de temperatura y tokens desde la interfaz
- **Herramientas especializadas** (productos, horarios, información corporativa)
- **ETL Pipeline** para scraping y procesamiento de datos
- **Interfaz Streamlit** minimalista y profesional
- **Múltiples proveedores LLM**: OpenAI, Google Gemini, Ollama

## 🏗️ Arquitectura

El sistema sigue una **Arquitectura por Capas** (Layered Architecture) inspirada en **Clean Architecture**, no MVC tradicional:

```
┌──────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  src/views/                                          │   │
│  │  └─ streamlit_chat_view.py                          │   │
│  │     • Renderiza interfaz de usuario                 │   │
│  │     • Captura eventos del usuario                   │   │
│  │     • Muestra respuestas del chatbot                │   │
│  └──────────────────┬───────────────────────────────────┘   │
└─────────────────────┼────────────────────────────────────────┘
                      │
                      │ Llama métodos del controlador
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  src/controllers/                                    │   │
│  │  └─ chatbot_controller.py                           │   │
│  │     • Coordina flujo de conversación                │   │
│  │     • Valida inputs del usuario                     │   │
│  │     • Gestiona sesiones (thread_id)                 │   │
│  │     • Orquesta operaciones entre capas              │   │
│  └──────────────────┬───────────────────────────────────┘   │
└─────────────────────┼────────────────────────────────────────┘
                      │
                      │ Usa el modelo de dominio
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  src/models/                                         │   │
│  │  ├─ chatbot_model.py                                │   │
│  │  │   • Lógica del agente conversacional             │   │
│  │  │   • Configuración del LLM                        │   │
│  │  │   • Trimming de mensajes (middleware)            │   │
│  │  │   • Invocación del agente con tools              │   │
│  │  │                                                   │   │
│  │  ├─ memory/                                          │   │
│  │  │   └─ short_term_memory.py                        │   │
│  │  │       • Gestión de checkpointer PostgreSQL       │   │
│  │  │       • Generación de thread_id único            │   │
│  │  │       • Persistencia de estado de conversación   │   │
│  │  │                                                   │   │
│  │  ├─ retrieval/ (en desarrollo)                      │   │
│  │  │   ├─ vector_store.py                             │   │
│  │  │   ├─ embeddings.py                               │   │
│  │  │   └─ retriever.py                                │   │
│  │  │       • Base de datos vectorial (Chroma)         │   │
│  │  │       • Búsqueda por similitud semántica         │   │
│  │  │       • Generación de embeddings                 │   │
│  │  │                                                   │   │
│  │  └─ tools/                                           │   │
│  │      ├─ product_tools.py                            │   │
│  │      ├─ company_tools.py                            │   │
│  │      ├─ rag_tools.py (en desarrollo)                │   │
│  │      └─ registry.py                                 │   │
│  │          • Herramientas del agente                  │   │
│  │          • Funciones ejecutables por el LLM         │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                      │
                      │ Lee configuración
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                   CONFIGURATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  src/config/                                         │   │
│  │  ├─ settings.py      (Variables de entorno)         │   │
│  │  └─ prompts.py       (System prompts)               │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Responsabilidades por Capa

#### **Presentation Layer** (`views/`)
- Interfaz de usuario con Streamlit
- Captura de eventos del usuario
- Renderizado de mensajes y componentes UI
- **NO** contiene lógica de negocio

#### **Application Layer** (`controllers/`)
- Coordinación entre View y Model
- Validación de inputs del usuario
- Gestión de sesiones (thread_id único por conversación)
- Manejo de errores de negocio
- **NO** conoce detalles de UI ni persistencia

#### **Domain Layer** (`models/`)
- Lógica central del chatbot (agente LangChain)
- Configuración del modelo LLM (temperatura, tokens)
- Trimming de mensajes mediante middleware
- Invocación del agente con herramientas
- **NO** conoce detalles de presentación

##### **Infraestructura dentro de Domain**
- **memory/**: Persistencia de estado en PostgreSQL (checkpointer)
- **retrieval/**: Base de datos vectorial y búsqueda semántica (en desarrollo)
- **tools/**: Herramientas ejecutables del agente

#### **Configuration Layer** (`config/`)
- Variables de entorno y constantes
- System prompts del chatbot
- Configuración estática
- **Sin lógica de negocio ni side effects**

### Principios de Diseño Aplicados

- **Dependency Rule**: Las dependencias apuntan hacia adentro (View → Controller → Model)
- **Separation of Concerns**: Cada capa tiene una responsabilidad única
- **SOLID Principles**: Single Responsibility y Dependency Inversion
- **Testability**: Cada capa es testeable independientemente
- **Independence of Frameworks**: El dominio no depende de Streamlit


## � Flujo de Datos

### **Usuario envía un mensaje**

```
1. USER
   └─> Escribe mensaje en el chat de Streamlit

2. PRESENTATION LAYER (views/streamlit_chat_view.py)
   ├─> Captura input con st.chat_input()
   ├─> Agrega mensaje al historial local de la UI
   └─> Llama: controller.send_message(messages)

3. APPLICATION LAYER (controllers/chatbot_controller.py)
   ├─> Valida formato de mensajes
   ├─> Obtiene thread_id de la sesión
   └─> Llama: model.invoke(messages, thread_id)

4. DOMAIN LAYER (models/chatbot_model.py)
   ├─> Construye config con thread_id
   ├─> Aplica middleware de trimming (mantiene últimos 4 mensajes)
   ├─> Invoca agent.invoke() con tools disponibles
   └─> Agent decide si usar herramientas:
       ├─> search_knowledge_base() → retrieval/retriever.py (en desarrollo)
       │   └─> Vector DB busca documentos relevantes
       ├─> get_product_info() → tools/product_tools.py
       ├─> get_store_hours() → tools/company_tools.py
       └─> get_company_info() → tools/company_tools.py

5. INFRASTRUCTURE (memory/)
   ├─> PostgreSQL persiste checkpoint de la conversación
   └─> Guarda estado en tabla 'checkpoints'

6. RESPONSE FLOW (vuelta)
   Model → Controller → View
   └─> Respuesta se renderiza en chat con st.chat_message()
```

### **Actualización de configuración (temperatura/tokens)**

```
1. USER
   └─> Ajusta sliders en sidebar
   └─> Click en "Aplicar Cambios"

2. VIEW (streamlit_chat_view.py)
   └─> Llama: controller.update_model_config(temperature, max_tokens)

3. CONTROLLER (chatbot_controller.py)
   └─> Llama: model.update_model_config(temperature, max_tokens)

4. MODEL (chatbot_model.py)
   ├─> Valida rangos (temperature: 0.0-2.0, max_tokens > 0)
   ├─> Actualiza configuración interna
   ├─> Recrea instancia del LLM con nuevos parámetros
   └─> Recrea agente con el nuevo modelo
   
   • NO reinstancia el ChatbotModel completo
   • Mantiene la misma conexión a PostgreSQL
   • Preserva el thread_id de la sesión
```

### **Búsqueda RAG** (en desarrollo)

```
1. USER: "¿Qué productos tienen protección antibacterial?"

2. AGENT (LangChain)
   └─> Decide usar tool: search_knowledge_base()

3. TOOL (tools/rag_tools.py)
   └─> Llama: retriever.retrieve(query)

4. RETRIEVAL LAYER (retrieval/)
   ├─> embeddings.py: Genera embedding del query
   ├─> vector_store.py: Busca en Chroma por similitud
   └─> retriever.py: Formatea documentos encontrados

5. AGENT
   ├─> Recibe contexto relevante de la BD vectorial
   └─> Genera respuesta basada en contexto + LLM

6. RESPONSE → Controller → View → User
```

## 🔧 Tecnologías

### Core
- **Python 3.11+**: Lenguaje principal
- **LangChain**: Framework para LLMs y agentes
- **LangGraph**: Orquestación de grafos de agentes
- **Streamlit**: Interfaz de usuario

### LLMs
- **OpenAI GPT**: Modelos de lenguaje
- **Google Gemini**: Modelo alternativo
- **Ollama**: Modelos locales

### Persistencia
- **PostgreSQL**: Memoria de conversaciones (checkpoints)
- **Chroma**: Base de datos vectorial para RAG (en desarrollo)
- **Docker**: Containerización de PostgreSQL

### Herramientas
- **uv**: Gestor de paquetes Python ultrarrápido
- **Make**: Automatización de comandos
- **BeautifulSoup/Selenium**: Web scraping
- **Pydantic**: Validación de datos


## � Requisitos

- Python 3.11+
- Docker (para PostgreSQL)
- uv (gestor de paquetes ultrarrápido)
- Make (opcional, para comandos automatizados)

## 🚀 Instalación

### 1. Clonar el repositorio

```powershell
git clone <repository-url>
cd tecnicas_avanzadas_llm
```

### 2. Instalar dependencias con uv

```powershell
# Instalar uv si no lo tienes
pip install uv

# Instalar dependencias del proyecto
uv sync
```

### 3. Levantar base de datos PostgreSQL

```powershell
# Crear y ejecutar contenedor PostgreSQL
make db-start

# Verificar que está corriendo
make db-status
```

### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# LLM API Keys
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# PostgreSQL (memoria del chatbot)
DB_URI=postgresql://student:12345678@localhost:5442/uao_llm

# Vector Database (en desarrollo)
VECTOR_DB_PATH=./data/vector_db

# Logging
LOG_LEVEL=INFO
```

## ⚙️ Configuración

### Configurar el system prompt

Editar `src/config/prompts.py`:

```python
PROMPTS = {
    "colgate_palmolive_system": """
    Eres un asistente virtual experto en productos Colgate Palmolive...
    """
}
```

### Configurar herramientas (tools)

Las herramientas se definen en `src/models/tools/`:

- `product_tools.py`: Información de productos
- `company_tools.py`: Información corporativa (horarios, contacto)
- `rag_tools.py`: Búsqueda en base de conocimiento (en desarrollo)
- `registry.py`: Registro de todas las herramientas

## 🎮 Uso

### Iniciar la aplicación

```powershell
# Asegurarse que PostgreSQL está corriendo
make db-restart

# Ejecutar la aplicación Streamlit
uv run streamlit run main.py

# O usar el comando make
make start
```

La aplicación estará disponible en: `http://localhost:8501`

### Interfaz de usuario

1. **Chat principal**: Escribe mensajes y recibe respuestas del asistente
2. **Sidebar izquierdo**:
   - **Temperature**: Ajusta creatividad del modelo (0.0-2.0)
   - **Max Tokens**: Ajusta longitud de respuestas (100-4000)
   - **Aplicar Cambios**: Actualiza configuración sin perder historial
   - **Thread ID**: Identificador único de la conversación
   - **Nueva Conversación**: Reinicia con nuevo thread_id

## 📁 Estructura del Proyecto

```
tecnicas_avanzadas_llm/
├── main.py                       # Punto de entrada de la aplicación
├── Makefile                      # Comandos automatizados
├── pyproject.toml                # Configuración del proyecto y dependencias
├── .env                          # Variables de entorno (no versionado)
├── README.md
│
├── src/
│   ├── config/
│   │   ├── settings.py           # Configuración de variables de entorno
│   │   ├── prompts.py            # System prompts del chatbot
│   │   └── logger.py             # Configuración de logging
│   │
│   ├── models/
│   │   ├── chatbot_model.py      # Lógica principal del agente LangChain
│   │   │
│   │   ├── memory/               # Gestión de memoria persistente
│   │   │   ├── __init__.py
│   │   │   └── short_term_memory.py
│   │   │
│   │   ├── retrieval/            # Base de datos vectorial y RAG (en desarrollo)
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py
│   │   │   ├── embeddings.py
│   │   │   └── retriever.py
│   │   │
│   │   └── tools/                # Herramientas del agente
│   │       ├── __init__.py
│   │       ├── product_tools.py
│   │       ├── company_tools.py
│   │       ├── rag_tools.py      # En desarrollo
│   │       └── registry.py
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── chatbot_controller.py # Coordinación entre View y Model
│   │
│   ├── views/
│   │   ├── __init__.py
│   │   └── streamlit/
│   │       ├── __init__.py
│   │       └── streamlit_chat_view.py  # Interfaz de usuario Streamlit
│   │
│   └── processing/
│       └── chunking.py           # Procesamiento de documentos
│
├── etl/
│   ├── extract/                  # Scrapers
│   │   ├── __init__.py
│   │   ├── colgate_productos.py
│   │   ├── palmolive_productos.py
│   │   ├── colgate_palmolive.py
│   │   └── fetch_social_media.py
│   │
│   ├── transform/                # Procesamiento de datos
│   │   ├── __init__.py
│   │   ├── preprocessing.py
│   │   ├── plain_products_processing.py
│   │   ├── plain_youtube_processing.py
│   │   └── plain_company_processing.py
│   │
│   └── load/                     # Carga de datos (en desarrollo)
│
├── data/                         # Datos del proyecto
│   ├── raw/                      # Datos crudos del scraping
│   │   ├── productos_colgate.csv
│   │   ├── productos_palmolive.csv
│   │   ├── company_data.json
│   │   └── youtube_channel_videos.json
│   │
│   ├── processed/                # Datos procesados (texto plano)
│   │   ├── context_colgate.txt
│   │   ├── context_palmolive.txt
│   │   ├── context_youtube.txt
│   │   └── company_context.txt
│   │
│   ├── vector_db/                # Base de datos vectorial (en desarrollo)
│   └── qa/
│       └── qa_colgate_palmolive.csv
│
├── tests/                        # Tests unitarios (en desarrollo)
└── docs/                         # Documentación adicional
```

## �️ Comandos Make

### Base de datos (PostgreSQL)

```powershell
# Crear y ejecutar contenedor PostgreSQL
make db-start

# Detener el contenedor (sin eliminarlo)
make db-stop

# Reiniciar el contenedor existente
make db-restart

# Eliminar el contenedor completamente
make db-remove

# Ver logs del contenedor
make db-logs

# Conectarse con psql
make db-shell

# Resetear la BD (eliminar y crear de nuevo)
make db-reset

# Verificar estado del contenedor
make db-status
```

### ETL Pipeline

```powershell
# Scraping de productos
make scrape-palmolive      # Scraping de productos Palmolive
make scrape-colgate        # Scraping de productos Colgate
make scrape-all            # Scraping de todos los productos

# Procesamiento de datos
make preprocess            # Preprocesamiento general

# Procesamiento de archivos de texto
make txt-products-preprocess   # Procesar productos a texto plano
make txt-youtube-preprocess    # Procesar transcripciones YouTube
make txt-company-preprocess    # Procesar info corporativa
make txt-preprocess            # Procesar todos los archivos txt

# Chunking de documentos para vector DB (en desarrollo)
make chunk
```

### Iniciar aplicación

```powershell
# Reiniciar BD e iniciar aplicación Streamlit
make start
```

## 📊 ETL Pipeline

El sistema incluye un pipeline ETL completo para recolectar y procesar información:

### Pipeline Actual (sin RAG)

```mermaid
flowchart LR
  A[Web Scraping] --> B[Raw Data Storage]
  B --> C[Data Cleaning & Preprocessing]
  C --> D[Text Conversion]
  D --> E[Chatbot Tools]
  E --> F[Response Generation]
  F --> G[Streamlit Interface]
```

### Pipeline Futuro (con RAG)

```mermaid
flowchart LR
  A[Web Scraping] --> B[Raw Data Storage]
  B --> C[Data Cleaning]
  C --> D[Text Chunking]
  D --> E[Embedding Generation]
  E --> F[Vector DB Storage]
  F --> G[RAG Retrieval]
  G --> H[LLM Processing]
  H --> I[Response Generation]
  I --> J[Streamlit Interface]
```
### Pipeline Futuro (con RAG + Agent)

```mermaid
flowchart TD
    A[Ingesta desde data/processed] --> B[Chunking adaptativo con metadatos]
    B --> C[Embeddings Gemini: text-embedding-004]
    C --> D[Almacenamiento en Chroma: Vector DB]

    subgraph RAG Pipeline
        D --> E[Retriever con filtrado por tipo]
        E --> F[Tool: search_knowledge_base]
    end

    subgraph LangChain Orquestador
        F --> G[Agente Langchain]
        G --> H[Decisión: ¿usar herramienta o generar directamente?]
        H --> I[Generación de respuestas con grounding factual]
        I --> J[Persistencia en Postgres: memoria por thread_id]
        J --> K[Trimming de historial conversacional]
    end

    K --> L[Interfaz de usuario en Streamlit]
```

### 1. Extract (Scraping)

```powershell
# Scraping de productos Colgate y Palmolive
make scrape-all
```

**Extrae información de:**
- Productos Colgate (nombre, descripción, precio)
- Productos Palmolive (nombre, descripción, precio)
- Especificaciones técnicas
- Disponibilidad

**Archivos generados:**
- `data/raw/productos_colgate.csv`
- `data/raw/productos_palmolive.csv`

### 2. Transform (Procesamiento)

```powershell
# Preprocesar datos crudos
make preprocess

# Procesar archivos de texto plano
make txt-preprocess
```

**Procesamiento incluye:**
- Limpieza de texto (HTML, caracteres especiales)
- Normalización de formato
- Extracción de metadata
- Conversión a texto plano legible

**Archivos generados:**
- `data/processed/context_colgate.txt`
- `data/processed/context_palmolive.txt`
- `data/processed/company_context.txt`

### 3. Load (Chunking y Vectorización) - En Desarrollo

```powershell
# Crear chunks y cargar en vector DB
make chunk
```

**Proceso (futuro):**
- Divide documentos en chunks semánticos
- Genera embeddings con OpenAI/Google
- Almacena en Chroma (base de datos vectorial)
- Habilita búsqueda semántica para RAG

## � Notas de Desarrollo

### Agregar nuevas herramientas (tools)

1. Crear función en `src/tools/`:

```python
# src/models/tools/custom_tools.py
def my_custom_tool(param: str) -> str:
    """Descripción de la herramienta."""
    # Implementación
    return result
```

2. Registrar en `src/tools/registry.py`:

```python
from src.models.tools.custom_tools import my_custom_tool

def get_tools():
    tools = [
        # ...existing tools...
        Tool(
            name="my_custom_tool",
            func=my_custom_tool,
            description="Descripción clara para que el agente la use",
        ),
    ]
    return tools
```

### Modificar configuración del modelo

Editar valores por defecto en `src/views/streamlit_chat_view.py`:

```python
def initialize_controller():
    controller = ChatbotController(
        model_name="google_genai:gemini-2.5-flash",
        temperature=0.1,    # Modificar aquí
        max_tokens=1000,    # Modificar aquí
        system_prompt=PROMPTS["colgate_palmolive_system"],
    )
```

### Cambiar base de datos vectorial (futuro)

El sistema usará Chroma por defecto. Para cambiar a Pinecone o Weaviate:

1. Instalar librería: `uv add pinecone-client`
2. Modificar `src/retrieval/vector_store.py`
3. Actualizar configuración en `src/config/settings.py`


## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📚 Referencias

- LangChain Documentation. (2025). "LangChain: Building applications with LLMs." https://python.langchain.com/
- LangGraph Documentation. (2025). "LangGraph: Build stateful agents." https://langchain-ai.github.io/langgraph/
- Streamlit Documentation. (2025). "Streamlit: The fastest way to build data apps." https://streamlit.io/
- PostgreSQL Documentation. (2025). "PostgreSQL: The world's most advanced open source database." https://www.postgresql.org/
- Selenium Documentation. (2025). "Selenium WebDriver for browser automation." https://www.selenium.dev/
- BeautifulSoup Documentation. (2025). "Beautiful Soup: HTML/XML parsing library." https://www.crummy.com/software/BeautifulSoup/
- Clean Architecture. Robert C. Martin. (2017). Prentice Hall.

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.

## 👥 Autores

- Juan Jose Bonilla - 22502052
- Yan Carlos Cuaran Imbacuan - 22502591
- Nicolas Lozano Mazuera - 22500565
- Soren Acevedo - 22500566

Universidad Autónoma de Occidente

---

**Proyecto académico** - Técnicas Avanzadas de LLM - 2025
