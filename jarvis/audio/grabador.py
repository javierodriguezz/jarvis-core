"""
Captura de audio desde el micrófono (Fase 5).

Usa sounddevice, que graba usando el dispositivo de entrada por defecto del
sistema operativo -- el mismo que se configura en Windows (Configuración de
sonido -> Entrada).
"""

import time

import numpy as np
import sounddevice as sd

import config


def grabar_audio(duracion_segundos: float = 4.0) -> np.ndarray:
    """
    Graba audio del micrófono por defecto durante duracion_segundos.

    Muestra una cuenta regresiva antes de empezar a grabar, para darle tiempo
    al usuario de prepararse -- si no, se pierde el inicio de lo que dice.

    Regresa un arreglo de una dimensión con muestras en punto flotante entre
    -1.0 y 1.0, a la frecuencia definida en config.AUDIO_SAMPLE_RATE -- el
    formato que espera jarvis.audio.transcriptor.transcribir().
    """
    for segundos_restantes in (3, 2, 1):
        print(f"Grabando en {segundos_restantes}...")
        time.sleep(1)
    print("Habla ahora...")

    fs = config.AUDIO_SAMPLE_RATE
    audio = sd.rec(int(duracion_segundos * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()

    print("Grabación terminada.")
    return audio.flatten()
