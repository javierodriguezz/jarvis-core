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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Fase 5: entrada de voz. WHISPER_MODEL es el tamaño del modelo de faster-whisper
# ("tiny", "base", "small", ...) -- a mayor tamaño, más preciso y más lento.
# "base" es el punto medio razonable para correr en CPU. AUDIO_SAMPLE_RATE es
# la frecuencia de muestreo (muestras por segundo) con la que se graba del
# micrófono; 16000 Hz es lo que espera Whisper, no hace falta más.
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
AUDIO_SAMPLE_RATE = 16000

# Fase 6: salida de voz. PIPER_VOICE es el nombre de la voz de Piper a usar
# (ver https://github.com/rhasspy/piper para el catálogo completo). Los
# archivos de la voz (.onnx y .onnx.json) se descargan una sola vez a
# VOICES_DIR -- no se suben a git, igual que la base de datos o los logs.
PIPER_VOICE = os.getenv("PIPER_VOICE", "es_ES-davefx-medium")
VOICES_DIR = DATA_DIR / "voices"

# Fase 6.5: conexión a una IA en la nube (Gemini) para preguntas abiertas que
# ninguna herramienta local sabe responder. La clave se saca gratis en
# https://aistudio.google.com/apikey (es distinta de la suscripción de la app
# de Gemini). Por defecto está vacía a propósito: sin clave, la herramienta
# avisa en vez de fallar. GEMINI_MODEL se deja configurable porque los nombres
# de modelo de Google cambian seguido -- si un día responde 404, se corrige en
# .env sin tocar el código (la lección del tag equivocado de Ollama, Fase 3).
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
