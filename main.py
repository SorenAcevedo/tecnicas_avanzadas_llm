"""
Script de ejecución para la aplicación Streamlit.
"""

import sys
import subprocess

from dotenv import load_dotenv
from pathlib import Path

# Carga variables de entorno desde .env, priorizando sobre variables de sistema
load_dotenv(override=True)

from src.config.settings import settings


def run_streamlit():
    """
    Ejecuta la aplicación Streamlit.
    """
    # Ruta al archivo de la vista
    view_path = (
        Path(__file__).parent / "src" / "views" / "streamlit" / "streamlit_threaded_chat_view.py"
    )

    # Comando para ejecutar Streamlit
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(view_path),
        "--server.port=8501",
        "--server.headless=true",
    ]

    print("🚀 Iniciando aplicación Streamlit...")
    print(f"📂 Archivo: {view_path}")
    print(f"🌐 URL: http://localhost:8501")
    print("-" * 50)

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario.")
    except Exception as e:
        print(f"❌ Error al ejecutar Streamlit: {e}")


if __name__ == "__main__":
    run_streamlit()
