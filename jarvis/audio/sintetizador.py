"""
Síntesis de texto a voz (Fase 6), usando Piper localmente.

Igual que con el modelo de Whisper en transcriptor.py, la voz de Piper se
carga una sola vez (cache a nivel de módulo) porque cargarla desde disco
tarda; las llamadas siguientes reusan la misma instancia.
"""

import numpy as np
from piper import PiperVoice

import config

# Cache a nivel de módulo: None hasta que _obtener_voz() la llena la
# primera vez que se necesita. Las llamadas siguientes reusan esta misma voz.
_voz = None


def _obtener_voz() -> PiperVoice:
    """Carga la voz de Piper la primera vez que se llama; después regresa la ya cargada."""
    global _voz
    if _voz is None:
        modelo = config.VOICES_DIR / f"{config.PIPER_VOICE}.onnx"
        configuracion = config.VOICES_DIR / f"{config.PIPER_VOICE}.onnx.json"
        _voz = PiperVoice.load(modelo, configuracion)
    return _voz


def sintetizar(texto: str) -> tuple[np.ndarray, int]:
    """
    Convierte texto a audio hablado en español.

    Regresa una tupla (audio, sample_rate): audio es un arreglo de una
    dimensión en punto flotante (igual formato que grabador.grabar_audio),
    y sample_rate es la frecuencia de muestreo propia de la voz cargada
    (no necesariamente la misma que config.AUDIO_SAMPLE_RATE, que es la
    de entrada por micrófono).
    """
    voz = _obtener_voz()
    trozos = list(voz.synthesize(texto))
    audio = np.concatenate([trozo.audio_float_array for trozo in trozos])
    return audio, trozos[0].sample_rate
