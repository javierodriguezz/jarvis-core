"""
Transcripción de audio a texto (Fase 5), usando faster-whisper localmente.

El modelo se descarga una sola vez (queda cacheado en disco por huggingface_hub)
y se carga en memoria una sola vez por ejecución del programa: cargarlo tarda
unos segundos, así que no conviene repetirlo en cada llamada.
"""

import numpy as np
from faster_whisper import WhisperModel

import config

# Cache a nivel de módulo: None hasta que _obtener_modelo() lo llena la
# primera vez que se necesita. Las llamadas siguientes reusan este mismo objeto.
_modelo = None


def _obtener_modelo() -> WhisperModel:
    """Carga el modelo de Whisper la primera vez que se llama; después regresa el ya cargado."""
    global _modelo
    if _modelo is None:
        _modelo = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
    return _modelo


def transcribir(audio: np.ndarray) -> str:
    """
    Transcribe a texto en español un arreglo de audio (como el que regresa
    jarvis.audio.grabador.grabar_audio). Regresa una cadena vacía si no se
    detectó voz.
    """
    modelo = _obtener_modelo()
    segmentos, _info = modelo.transcribe(audio, language="es")
    return " ".join(segmento.text.strip() for segmento in segmentos).strip()
