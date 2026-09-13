"""
Pruebas del cliente de Gemini (jarvis/core/gemini_client.py).

Ninguna de estas pruebas sale a internet -- se reemplaza requests.post con
una versión falsa. Así corren rápido, funcionan sin conexión, y no gastan la
cuota gratuita de la API con cada 'pytest'.
"""

import pytest
import requests

import config
from jarvis.core import gemini_client


def _respuesta_normal(*textos):
    """Arma el JSON que devuelve la API de Gemini para una respuesta con texto."""
    return {"candidates": [{"content": {"parts": [{"text": t} for t in textos]}}]}


class _RespuestaFalsaOk:
    def __init__(self, datos):
        self._datos = datos

    def raise_for_status(self):
        pass

    def json(self):
        return self._datos


class _RespuestaFalsaConError:
    def raise_for_status(self):
        raise requests.HTTPError("404 Not Found")


def test_generar_manda_la_pregunta_y_la_clave_correctas(monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "clave-de-prueba")
    peticiones = []

    def post_falso(url, headers, json, timeout):
        peticiones.append(
            {"url": url, "headers": headers, "json": json, "timeout": timeout}
        )
        return _RespuestaFalsaOk(_respuesta_normal("La capital es Canberra."))

    monkeypatch.setattr(gemini_client.requests, "post", post_falso)

    resultado = gemini_client.generar("cuál es la capital de Australia")

    assert resultado == "La capital es Canberra."
    assert peticiones[0]["url"].endswith(f"/{config.GEMINI_MODEL}:generateContent")
    assert peticiones[0]["headers"]["x-goog-api-key"] == "clave-de-prueba"
    assert peticiones[0]["json"] == {
        "contents": [{"parts": [{"text": "cuál es la capital de Australia"}]}]
    }


def test_generar_manda_la_instruccion_de_sistema_cuando_se_le_da(monkeypatch):
    peticiones = []

    def post_falso(url, headers, json, timeout):
        peticiones.append(json)
        return _RespuestaFalsaOk(_respuesta_normal("ok"))

    monkeypatch.setattr(gemini_client.requests, "post", post_falso)

    gemini_client.generar("hola", "responde en texto plano")

    assert peticiones[0]["systemInstruction"] == {
        "parts": [{"text": "responde en texto plano"}]
    }


def test_generar_sin_instruccion_no_manda_el_campo(monkeypatch):
    peticiones = []

    def post_falso(url, headers, json, timeout):
        peticiones.append(json)
        return _RespuestaFalsaOk(_respuesta_normal("ok"))

    monkeypatch.setattr(gemini_client.requests, "post", post_falso)

    gemini_client.generar("hola")

    assert "systemInstruction" not in peticiones[0]


def test_generar_une_las_partes_de_la_respuesta(monkeypatch):
    # Gemini a veces parte una misma respuesta en varios trozos de texto.
    monkeypatch.setattr(
        gemini_client.requests,
        "post",
        lambda *a, **k: _RespuestaFalsaOk(_respuesta_normal("Hola ", "Javier.")),
    )

    assert gemini_client.generar("saluda") == "Hola Javier."


def test_generar_falla_si_no_hay_candidatos(monkeypatch):
    # Pasa de verdad cuando los filtros de seguridad de Gemini bloquean algo:
    # contesta 200, pero sin candidatos.
    monkeypatch.setattr(
        gemini_client.requests, "post", lambda *a, **k: _RespuestaFalsaOk({})
    )

    with pytest.raises(ValueError):
        gemini_client.generar("algo")


def test_generar_falla_si_la_respuesta_no_trae_texto(monkeypatch):
    sin_texto = {"candidates": [{"content": {"parts": []}}]}
    monkeypatch.setattr(
        gemini_client.requests, "post", lambda *a, **k: _RespuestaFalsaOk(sin_texto)
    )

    with pytest.raises(ValueError):
        gemini_client.generar("algo")


def test_generar_propaga_error_http(monkeypatch):
    monkeypatch.setattr(
        gemini_client.requests, "post", lambda *a, **k: _RespuestaFalsaConError()
    )

    with pytest.raises(requests.HTTPError):
        gemini_client.generar("algo")


def test_generar_propaga_error_de_conexion(monkeypatch):
    def post_que_falla(*args, **kwargs):
        raise requests.ConnectionError("sin internet")

    monkeypatch.setattr(gemini_client.requests, "post", post_que_falla)

    with pytest.raises(requests.ConnectionError):
        gemini_client.generar("algo")
