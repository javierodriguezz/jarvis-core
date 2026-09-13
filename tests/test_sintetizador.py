"""
Pruebas de síntesis de voz (jarvis/audio/sintetizador.py).

Ninguna de estas pruebas carga una voz de Piper real -- se reemplaza
PiperVoice por una versión falsa, así corren rápido y no dependen de tener
el modelo de voz descargado ni de esperar la síntesis real.
"""

import numpy as np
import pytest

from jarvis.audio import sintetizador


class _TrozoFalso:
    def __init__(self, audio, sample_rate=22050):
        self.audio_float_array = audio
        self.sample_rate = sample_rate


class _VozFalsa:
    def __init__(self, trozos):
        self._trozos = trozos

    def synthesize(self, texto):
        return iter(self._trozos)


@pytest.fixture(autouse=True)
def _sin_voz_cacheada(monkeypatch):
    # Cada prueba arranca sin voz en cache, para no depender del orden de ejecución.
    monkeypatch.setattr(sintetizador, "_voz", None)


def test_sintetizar_concatena_los_trozos_de_audio(monkeypatch):
    trozos = [
        _TrozoFalso(np.array([1.0, 2.0], dtype=np.float32)),
        _TrozoFalso(np.array([3.0], dtype=np.float32)),
    ]
    voz_falsa = _VozFalsa(trozos)
    monkeypatch.setattr(sintetizador.PiperVoice, "load", lambda *a, **k: voz_falsa)

    audio, sample_rate = sintetizador.sintetizar("hola mundo")

    np.testing.assert_array_equal(audio, np.array([1.0, 2.0, 3.0], dtype=np.float32))
    assert sample_rate == 22050


def test_sintetizar_reutiliza_la_voz_ya_cargada_en_vez_de_recrearla(monkeypatch):
    contador = {"veces": 0}
    voz_falsa = _VozFalsa([_TrozoFalso(np.zeros(1, dtype=np.float32))])

    def carga_falsa(*args, **kwargs):
        contador["veces"] += 1
        return voz_falsa

    monkeypatch.setattr(sintetizador.PiperVoice, "load", carga_falsa)

    sintetizador.sintetizar("hola")
    sintetizador.sintetizar("mundo")

    assert contador["veces"] == 1
