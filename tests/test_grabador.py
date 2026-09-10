"""
Pruebas de captura de audio (jarvis/audio/grabador.py).

Ninguna de estas pruebas usa un micrófono real -- se reemplazan
sounddevice.rec/wait y time.sleep por versiones falsas, así corren rápido y
no dependen de que haya un micrófono conectado a la máquina.
"""

import numpy as np

import config
from jarvis.audio import grabador


def test_grabar_audio_pide_las_muestras_correctas_y_regresa_arreglo_plano(monkeypatch):
    llamadas = {}

    def rec_falso(n_muestras, samplerate, channels, dtype):
        llamadas["n_muestras"] = n_muestras
        llamadas["samplerate"] = samplerate
        llamadas["channels"] = channels
        llamadas["dtype"] = dtype
        return np.zeros((n_muestras, channels), dtype=np.float32)

    monkeypatch.setattr(grabador.sd, "rec", rec_falso)
    monkeypatch.setattr(grabador.sd, "wait", lambda: None)
    monkeypatch.setattr(grabador.time, "sleep", lambda segundos: None)

    audio = grabador.grabar_audio(duracion_segundos=2)

    assert llamadas["n_muestras"] == 2 * config.AUDIO_SAMPLE_RATE
    assert llamadas["samplerate"] == config.AUDIO_SAMPLE_RATE
    assert llamadas["channels"] == 1
    assert llamadas["dtype"] == "float32"
    assert audio.shape == (2 * config.AUDIO_SAMPLE_RATE,)


def test_grabar_audio_usa_duracion_por_defecto(monkeypatch):
    llamadas = {}

    def rec_falso(n_muestras, samplerate, channels, dtype):
        llamadas["n_muestras"] = n_muestras
        return np.zeros((n_muestras, channels), dtype=np.float32)

    monkeypatch.setattr(grabador.sd, "rec", rec_falso)
    monkeypatch.setattr(grabador.sd, "wait", lambda: None)
    monkeypatch.setattr(grabador.time, "sleep", lambda segundos: None)

    grabador.grabar_audio()

    assert llamadas["n_muestras"] == 4 * config.AUDIO_SAMPLE_RATE
