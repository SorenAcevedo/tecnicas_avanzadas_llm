"""
Loader de configuración de modelos LLM.
Carga los modelos disponibles para cada proveedor desde un archivo YAML.

Uso:
    from src.core.config.model_loader import load_model_config
    config = load_model_config()
    modelos_ollama = config['ollama']['models']
"""

import yaml
import os

def load_model_config(config_path=None):
    """
    Carga la configuración de modelos LLM desde un archivo YAML.
    Args:
        config_path (str, opcional): Ruta al archivo de configuración YAML. Si no se especifica, usa config/models.yaml.
    Returns:
        dict: Diccionario con los modelos disponibles por proveedor.
    """
    if config_path is None:
        # Busca la carpeta 'config' en la raíz del workspace
        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        config_path = os.path.join(workspace_dir, 'config', 'models.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
