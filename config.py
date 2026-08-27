"""
Carga de configuración del proyecto.

Por ahora solo define rutas base. Cuando lleguemos a la Fase 3 (Ollama)
agregaremos aquí la carga de variables de entorno desde .env usando
python-dotenv -- lo explicamos en su momento, no hace falta entenderlo todavía.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Carpetas donde el asistente SÍ puede buscar archivos (Fase 1, herramienta de búsqueda).
# Lista blanca explícita: nunca buscamos en todo el disco.
ALLOWED_SEARCH_DIRS = [
    str(Path.home() / "Desktop"),
    str(Path.home() / "Downloads"),
]
