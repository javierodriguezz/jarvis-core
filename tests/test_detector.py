"""
Pruebas de la palabra de activación (jarvis/audio/detector.py).

Ninguna prueba abre el micrófono ni carga el modelo real de openWakeWord:
se reemplazan sd.InputStream y Model por dobles, así la suite corre rápido
y no depende del hardware ni de tener los modelos descargados.
"""

import numpy as np
import pytest

import config
from jarvis.audio import detector


class _SeAcaboElAudio(Exception):
    """La usa _StreamFalso para avisar que el detector siguió escuchando de más."""


class _StreamFalso:
    """Imita a sounddevice.InputStream: se usa con 'with' y entrega bloques de audio."""

    def __init__(self, bloques, **kwargs):
        self._bloques = list(bloques)
        self.kwargs = kwargs
        self.lecturas = 0
        self.cerrado = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cerrado = True
        return False

    def read(self, muestras):
        if not self._bloques:
            raise _SeAcaboElAudio("el detector pidió más audio del esperado")
        self.lecturas += 1
        return self._bloques.pop(0), False


class _ModeloFalso:
    """Imita al Model de openWakeWord: regresa un puntaje fijo por cada bloque."""

    def __init__(self, puntajes):
        self._puntajes = list(puntajes)
        self.reseteos = 0

    def reset(self):
        self.reseteos += 1

    def predict(self, audio):
        puntaje = self._puntajes.pop(0) if self._puntajes else 0.0
        return {config.WAKEWORD_MODEL: puntaje}


def _bloques(cuantos):
    """Genera 'cuantos' bloques de audio silencioso del tamaño que lee el detector."""
    return [np.zeros((detector.CHUNK_MUESTRAS, 1), dtype=np.int16) for _ in range(cuantos)]


@pytest.fixture(autouse=True)
def _sin_modelo_cacheado(monkeypatch):
    # Cada prueba arranca sin modelo en cache, para no depender del orden de ejecución.
    monkeypatch.setattr(detector, "_modelo", None)


def _preparar(monkeypatch, puntajes, bloques_disponibles):
    """Enchufa un modelo y un stream falsos, y los regresa para poder revisarlos."""
    modelo_falso = _ModeloFalso(puntajes)
    monkeypatch.setattr(detector, "Model", lambda *a, **k: modelo_falso)

    creados = []

    def constructor_de_stream(**kwargs):
        stream = _StreamFalso(_bloques(bloques_disponibles), **kwargs)
        creados.append(stream)
        return stream

    monkeypatch.setattr(detector.sd, "InputStream", constructor_de_stream)
    return modelo_falso, creados


def test_regresa_en_cuanto_el_puntaje_cruza_el_umbral(monkeypatch):
    # Los dos primeros bloques son ruido; en el tercero se oye la frase.
    _modelo, streams = _preparar(monkeypatch, [0.01, 0.2, 0.99], bloques_disponibles=10)

    detector.esperar_palabra_activacion()

    # Leyó exactamente 3 bloques: dejó de escuchar en cuanto detectó.
    assert streams[0].lecturas == 3


def test_sigue_escuchando_mientras_el_puntaje_no_alcanza_el_umbral(monkeypatch):
    # Puntajes altos pero por debajo del umbral: no deben activar nada.
    _preparar(monkeypatch, [0.49, 0.49, 0.49], bloques_disponibles=3)

    with pytest.raises(_SeAcaboElAudio):
        detector.esperar_palabra_activacion()


def test_el_umbral_es_inclusivo(monkeypatch):
    _modelo, streams = _preparar(
        monkeypatch, [config.WAKEWORD_THRESHOLD], bloques_disponibles=5
    )

    detector.esperar_palabra_activacion()

    assert streams[0].lecturas == 1


def test_cierra_el_microfono_al_terminar(monkeypatch):
    _modelo, streams = _preparar(monkeypatch, [0.99], bloques_disponibles=1)

    detector.esperar_palabra_activacion()

    assert streams[0].cerrado


def test_abre_el_microfono_en_int16_y_no_en_float32(monkeypatch):
    # openWakeWord espera enteros de 16 bits; con float32 nunca detectaría nada.
    _modelo, streams = _preparar(monkeypatch, [0.99], bloques_disponibles=1)

    detector.esperar_palabra_activacion()

    assert streams[0].kwargs["dtype"] == "int16"
    assert streams[0].kwargs["samplerate"] == config.AUDIO_SAMPLE_RATE


def test_limpia_el_buffer_del_modelo_antes_de_escuchar(monkeypatch):
    modelo_falso, _streams = _preparar(monkeypatch, [0.99], bloques_disponibles=1)

    detector.esperar_palabra_activacion()

    assert modelo_falso.reseteos == 1


def test_reutiliza_el_modelo_ya_cargado_en_vez_de_recrearlo(monkeypatch):
    contador = {"veces": 0}
    modelo_falso = _ModeloFalso([0.99, 0.99])

    def constructor_falso(*args, **kwargs):
        contador["veces"] += 1
        return modelo_falso

    monkeypatch.setattr(detector, "Model", constructor_falso)
    monkeypatch.setattr(
        detector.sd, "InputStream", lambda **k: _StreamFalso(_bloques(1), **k)
    )

    detector.esperar_palabra_activacion()
    detector.esperar_palabra_activacion()

    assert contador["veces"] == 1
