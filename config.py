"""
Carga de configuración del proyecto.

Define rutas base y, desde la Fase 3, carga variables de entorno desde
.env usando python-dotenv (por ejemplo, qué modelo de Ollama usar).
"""

from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

load_dotenv(BASE_DIR / ".env")

# Carpetas donde el asistente SÍ puede buscar archivos (Fase 1, herramienta de búsqueda).
# Lista blanca explícita: nunca buscamos en todo el disco.
ALLOWED_SEARCH_DIRS = [
    str(Path.home() / "Desktop"),
    str(Path.home() / "Downloads"),
]

# Programas que el asistente puede abrir (Fase 1, herramienta "abrir programa o web").
# La clave es la palabra que usa el usuario; el valor es el ejecutable exacto que se
# pasa a subprocess.Popen como lista (nunca como texto libre en una shell).
PROGRAMAS_PERMITIDOS = {
    "bloc de notas": "notepad.exe",
    "calculadora": "calc.exe",
    "explorador": "explorer.exe",
}

# Páginas web que el asistente puede abrir. La clave es la palabra que usa el
# usuario; el valor es la URL exacta que se pasa a webbrowser.open().
SITIOS_PERMITIDOS = {
    "youtube": "https://youtube.com",
    "github": "https://github.com",
}

# Fase 3: servicio local de Ollama (debe estar corriendo en la máquina) y
# el modelo que se le pide. OLLAMA_HOST no lleva ninguna ruta al final --
# cada función de llm_client.py agrega la suya (ej. /api/generate). Ambos
# valores se pueden sobreescribir en .env (ver .env.example); si no está
# definido ahí, se usa el valor por defecto de la derecha.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
