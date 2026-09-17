"""
Detección de la palabra de activación (Fase 7), usando openWakeWord.

A diferencia de Whisper, este modelo no transcribe nada: solo contesta, muchas
veces por segundo, qué tan seguro está de haber oído la frase de activación.
Es lo bastante ligero (unos milisegundos por cada 80 ms de audio) como para
dejarlo escuchando de forma continua, cosa que con Whisper sería inviable.

El modelo se carga una sola vez por ejecución, mismo patrón que
jarvis.audio.transcriptor y jarvis.audio.sintetizador.
"""

import numpy as np
import sounddevice as sd
from openwakeword.model import Model

import config

# openWakeWord procesa el audio en bloques de exactamente 1280 muestras.
# A config.AUDIO_SAMPLE_RATE (16000 muestras por segundo) eso equivale a 80 ms.
CHUNK_MUESTRAS = 1280

# Cache a nivel de módulo: None hasta la primera llamada a _obtener_modelo().
_modelo = None


def _obtener_modelo() -> Model:
    """Carga el modelo de openWakeWord la primera vez; después regresa el ya cargado."""
    global _modelo
    if _modelo is None:
        _modelo = Model(
            wakeword_models=[config.WAKEWORD_MODEL], inference_framework="onnx"
        )
    return _modelo


def esperar_palabra_activacion() -> None:
    """
    Abre el micrófono y se queda escuchando hasta oír la palabra de activación.

    Bloquea: no regresa hasta detectarla (o hasta que el usuario interrumpa con
    Ctrl+C, que sube como KeyboardInterrupt). El micrófono se cierra al salir,
    para que Jarvis no se oiga a sí mismo mientras responde en voz alta.

    El audio se lee en int16 porque es el formato que espera openWakeWord --
    distinto del float32 que usa jarvis.audio.grabador para Whisper.
    """
    modelo = _obtener_modelo()
    # Limpia el buffer interno del modelo: si no, los restos de la activación
    # anterior podrían disparar una detección nueva de inmediato.
    modelo.reset()

    with sd.InputStream(
        samplerate=config.AUDIO_SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_MUESTRAS,
    ) as stream:
        while True:
            audio, _hubo_perdida = stream.read(CHUNK_MUESTRAS)
            puntajes = modelo.predict(np.asarray(audio).flatten())
            if puntajes[config.WAKEWORD_MODEL] >= config.WAKEWORD_THRESHOLD:
                return
