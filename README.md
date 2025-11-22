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
- [Tecnologías](#tecnologías)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Comandos Make](#comandos-make)
- [ETL Pipeline](#etl-pipeline)
- [Referencias](#referencias)

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

```mermaid
graph TB
    subgraph PRESENTATION["🎨 PRESENTATION LAYER"]
        VIEW["src/views/<br/>streamlit_chat_view.py"]
        VIEW_DESC["• Renderiza interfaz de usuario<br/>• Captura eventos del usuario<br/>• Muestra respuestas del chatbot"]
    end

    subgraph APPLICATION["⚙️ APPLICATION LAYER"]
        CTRL["src/controllers/<br/>chatbot_controller.py"]
        CTRL_DESC["• Coordina flujo de conversación<br/>• Valida inputs del usuario<br/>• Gestiona sesiones thread_id<br/>• Orquesta operaciones entre capas"]
    end

    subgraph DOMAIN["🧠 DOMAIN LAYER"]
        MODEL["src/models/<br/>chatbot_model.py"]
        MODEL_DESC["• Lógica del agente conversacional<br/>• Configuración del LLM<br/>• Trimming de mensajes middleware<br/>• Invocación del agente con tools"]
        
        MEMORY["src/memory/<br/>short_term_memory.py"]
        MEMORY_DESC["• Checkpointer PostgreSQL<br/>• Generación de thread_id único<br/>• Persistencia de estado"]
        
        RETRIEVAL["src/retrieval/<br/>vector_store.py, embeddings.py"]
        RETRIEVAL_DESC["• Base de datos vectorial Chroma<br/>• Búsqueda por similitud semántica<br/>• Generación de embeddings"]
        
        TOOLS["src/tools/<br/>faq_tool.py, retrieve_tool.py, price_tool.py"]
        TOOLS_DESC["• Herramientas del agente<br/>• Funciones ejecutables por el LLM"]
    end

    subgraph CONFIG["📝 CONFIGURATION LAYER"]
        SETTINGS["src/config/<br/>settings.py, prompts.py"]
        SETTINGS_DESC["• Variables de entorno<br/>• System prompts del chatbot"]
    end

    subgraph INFRA["💾 INFRASTRUCTURE"]
        POSTGRES[("PostgreSQL<br/>Checkpoints")]
        CHROMA[("ChromaDB<br/>Vector Store")]
        LLM["LLM APIs<br/>OpenAI/Gemini/Ollama"]
    end

    VIEW -->|send_message| CTRL
    CTRL -->|invoke| MODEL
    MODEL -->|usa| MEMORY
    MODEL -->|usa| TOOLS
    MODEL -->|usa| RETRIEVAL
    MEMORY -->|persiste| POSTGRES
    RETRIEVAL -->|consulta| CHROMA
    MODEL -->|llama| LLM
    MODEL -->|lee| SETTINGS
    CTRL -->|lee| SETTINGS

    style PRESENTATION fill:#e1f5ff
    style APPLICATION fill:#fff3e0
    style DOMAIN fill:#f3e5f5
    style CONFIG fill:#e8f5e9
    style INFRA fill:#fce4ec
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

##  Requisitos

- Python 3.12+
- Docker (para PostgreSQL)
- uv (gestor de paquetes ultrarrápido)
- Make (opcional, para comandos automatizados)

## 🔧 Tecnologías

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

Editar `src/config/prompts.py` para personalizar el system prompt:

```python
PROMPTS = {
    "colgate_palmolive_system": """
    Eres un asistente virtual experto en productos Colgate Palmolive...
    """
}
```

## 🎮 Uso

### Iniciar la aplicación

```powershell
# Asegurarse que PostgreSQL está corriendo
make db-restart

# Usar el comando make
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
│   │       ├── faq_tool.py
│   │       ├── retrieve_tool.py
│   │       ├── price_tool.py
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
│   │   ├── plain_company_processing.py
│   │   └── price_processing.py   # Procesamiento de precios
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
│       ├── qa_colgate_palmolive.csv
│       ├── faq.json
│       └── prices.json           # Precios consolidados de productos
│
├── tests/                        # Tests unitarios (en desarrollo)
└── docs/                         # Documentación adicional
```

## 🛠️ Comandos Make

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

### Herramientas del Agente

El chatbot cuenta con herramientas especializadas que el LLM puede invocar automáticamente:

#### 1. **FAQ Tool** (`faq_tool.py`)
Busca respuestas en preguntas frecuentes usando coincidencia aproximada.

```python
faq_tool(faq_input: FaqInput) -> str
```

**Ejemplo:**
- Usuario: "¿Cuál es el horario de atención?"
- Tool: Busca en `data/qa/faq.json` y retorna la respuesta más similar

#### 2. **Retrieve Tool** (`retrieve_tool.py`)
Búsqueda semántica en la base de conocimiento usando RAG.

```python
retrieve_tool(retrieve_input: RetrieveInput) -> str
```

**Ejemplo:**
- Usuario: "Cuéntame sobre los productos de blanqueamiento"
- Tool: Busca en ChromaDB y retorna información relevante

#### 3. **Price Tool** (`price_tool.py`)
Consulta precios de productos Colgate y Palmolive en diferentes tiendas.

```python
price_tool(price_input: PriceInput) -> str
```

**Características:**
- Búsqueda fuzzy de productos por nombre
- Comparación de precios entre tiendas
- Información de disponibilidad
- Identificación automática de mejor oferta
- Filtrado por tienda específica

**Ejemplos:**
- Usuario: "¿Cuánto cuesta la crema dental Colgate Total?"
- Tool: Retorna precios en todas las tiendas disponibles
- Usuario: "¿Cuál es el precio en Éxito del jabón Palmolive?"
- Tool: Filtra y muestra solo precios de ExitoCO

**Tiendas soportadas:** ExitoCO, JumboCO, OlimpicaCO, FarmatodoCO, LaRebajaVirtualCO, MerqueoCO

**Procesamiento de datos:** Para actualizar precios, ejecutar:
```powershell
python etl/transform/price_processing.py
```

### Iniciar aplicación

```powershell
# Reiniciar BD e iniciar aplicación Streamlit
make start
```

## Tecnologías

### Core
- **Python 3.12+**: Lenguaje principal
- **LangChain & LangGraph**: Framework para LLMs y agentes
- **Streamlit**: Interfaz de usuario

### LLMs
- **OpenAI GPT**: Modelos de lenguaje
- **Google Gemini**: Modelo alternativo
- **Ollama**: Modelos locales

### Persistencia
- **PostgreSQL**: Memoria de conversaciones (checkpoints)
- **Chroma**: Base de datos vectorial para RAG
- **Docker**: Containerización de servicios

### Herramientas
- **uv**: Gestor de paquetes Python ultrarrápido
- **Make**: Automatización de comandos
- **BeautifulSoup/Selenium**: Web scraping
- **Pydantic**: Validación de datos

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

---

**Universidad Autónoma de Occidente** - Técnicas Avanzadas de LLM - 2025
