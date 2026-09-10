"""
Pruebas de transcripción (jarvis/audio/transcriptor.py).

Ninguna de estas pruebas carga un modelo de Whisper real -- se reemplaza
WhisperModel por una versión falsa, así corren rápido y no dependen de tener
el modelo descargado ni de esperar la inferencia real.
"""

import numpy as np
import pytest

from jarvis.audio import transcriptor


class _SegmentoFalso:
    def __init__(self, texto):
        self.text = texto


class _ModeloFalso:
    def __init__(self, segmentos_texto):
        self._segmentos_texto = segmentos_texto

    def transcribe(self, audio, language):
        segmentos = [_SegmentoFalso(t) for t in self._segmentos_texto]
        return segmentos, object()


@pytest.fixture(autouse=True)
def _sin_modelo_cacheado(monkeypatch):
    # Cada prueba arranca sin modelo en cache, para no depender del orden de ejecución.
    monkeypatch.setattr(transcriptor, "_modelo", None)


def test_transcribir_une_los_segmentos_y_quita_espacios(monkeypatch):
    modelo_falso = _ModeloFalso([" hola ", "mundo "])
    monkeypatch.setattr(transcriptor, "WhisperModel", lambda *a, **k: modelo_falso)

    resultado = transcriptor.transcribir(np.zeros(16000, dtype=np.float32))

    assert resultado == "hola mundo"


def test_transcribir_regresa_vacio_sin_segmentos(monkeypatch):
    modelo_falso = _ModeloFalso([])
    monkeypatch.setattr(transcriptor, "WhisperModel", lambda *a, **k: modelo_falso)

    resultado = transcriptor.transcribir(np.zeros(16000, dtype=np.float32))

    assert resultado == ""


def test_transcribir_reutiliza_el_modelo_ya_cargado_en_vez_de_recrearlo(monkeypatch):
    contador = {"veces": 0}

    def constructor_falso(*args, **kwargs):
        contador["veces"] += 1
        return _ModeloFalso(["hola"])

    monkeypatch.setattr(transcriptor, "WhisperModel", constructor_falso)

    transcriptor.transcribir(np.zeros(16000, dtype=np.float32))
    transcriptor.transcribir(np.zeros(16000, dtype=np.float32))

    assert contador["veces"] == 1
