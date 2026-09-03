"""
Pruebas del cliente de Ollama (jarvis/core/llm_client.py).

Ninguna de estas pruebas habla de verdad con Ollama -- se reemplaza
requests.post con una versión falsa, así las pruebas corren igual de rápido
y confiable con o sin el servicio de Ollama corriendo.
"""

import pytest
import requests

import config
from jarvis.core import llm_client


class _RespuestaFalsaOk:
    def __init__(self, texto):
        self._texto = texto

    def raise_for_status(self):
        pass

    def json(self):
        return {"response": self._texto}


class _RespuestaFalsaConError:
    def raise_for_status(self):
        raise requests.HTTPError("500 Server Error")


def test_generar_manda_el_prompt_correcto(monkeypatch):
    peticiones = []

    def post_falso(url, json, timeout):
        peticiones.append({"url": url, "json": json, "timeout": timeout})
        return _RespuestaFalsaOk("hola")

    monkeypatch.setattr(llm_client.requests, "post", post_falso)

    resultado = llm_client.generar("di hola")

    assert resultado == "hola"
    assert peticiones[0]["url"] == f"{config.OLLAMA_HOST}/api/generate"
    assert peticiones[0]["json"] == {
        "model": config.OLLAMA_MODEL,
        "prompt": "di hola",
        "stream": False,
    }


def test_generar_propaga_error_http(monkeypatch):
    monkeypatch.setattr(
        llm_client.requests, "post", lambda *args, **kwargs: _RespuestaFalsaConError()
    )

    with pytest.raises(requests.HTTPError):
        llm_client.generar("algo")


def test_generar_propaga_error_de_conexion(monkeypatch):
    def post_que_falla(*args, **kwargs):
        raise requests.ConnectionError("no se pudo conectar")

    monkeypatch.setattr(llm_client.requests, "post", post_que_falla)

    with pytest.raises(requests.ConnectionError):
        llm_client.generar("algo")
