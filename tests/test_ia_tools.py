"""
Pruebas de la herramienta preguntar_ia (jarvis/tools/ia_tools.py).

Ninguna prueba habla con Gemini de verdad: se reemplaza gemini_client.generar
por una versión falsa. Lo que se prueba aquí es la capa de arriba -- qué le
contesta Jarvis al usuario en cada situación -- no el cliente HTTP, que ya
tiene sus propias pruebas en test_gemini_client.py.
"""

import pytest
import requests

import config
from jarvis.tools import ia_tools


class _RespuestaHttp:
    """Lo mínimo de una respuesta de requests para probar _codigo_http."""

    def __init__(self, status_code):
        self.status_code = status_code


@pytest.fixture(autouse=True)
def _con_clave_configurada(monkeypatch):
    # Casi todas las pruebas asumen que ya hay clave; la prueba del caso "sin
    # clave" la vuelve a vaciar por su cuenta.
    monkeypatch.setattr(config, "GEMINI_API_KEY", "clave-de-prueba")


def _falla_con(monkeypatch, excepcion):
    """Hace que gemini_client.generar levante la excepción indicada."""

    def generar_que_falla(pregunta, instruccion_sistema=None):
        raise excepcion

    monkeypatch.setattr(ia_tools.gemini_client, "generar", generar_que_falla)


def _responde_con(monkeypatch, texto):
    """Hace que gemini_client.generar regrese un texto fijo, sin salir a internet."""
    monkeypatch.setattr(
        ia_tools.gemini_client,
        "generar",
        lambda pregunta, instruccion_sistema=None: texto,
    )


def test_preguntar_ia_regresa_la_respuesta_de_gemini(monkeypatch):
    _responde_con(monkeypatch, "Canberra.")

    assert ia_tools.preguntar_ia("capital de Australia") == "Canberra."


def test_preguntar_ia_le_pide_al_modelo_que_hable_en_texto_plano(monkeypatch):
    recibido = {}

    def generar_falso(pregunta, instruccion_sistema=None):
        recibido["pregunta"] = pregunta
        recibido["instruccion"] = instruccion_sistema
        return "ok"

    monkeypatch.setattr(ia_tools.gemini_client, "generar", generar_falso)

    ia_tools.preguntar_ia("qué es una API")

    assert recibido["pregunta"] == "qué es una API"
    assert "voz alta" in recibido["instruccion"]


def test_preguntar_ia_quita_el_markdown_de_la_respuesta(monkeypatch):
    # Gemini responde con negritas aunque se le pida texto plano, y Piper
    # terminaría dictando los asteriscos en voz alta.
    _responde_con(monkeypatch, "La capital es **Ulán Bator**, también escrita *Ulaanbaatar*.")

    resultado = ia_tools.preguntar_ia("capital de Mongolia")

    assert "*" not in resultado
    assert "Ulán Bator" in resultado


def test_preguntar_ia_quita_encabezados_y_acentos_graves(monkeypatch):
    _responde_con(monkeypatch, "## Resumen\nUsa el comando `pytest` para correr las pruebas.")

    resultado = ia_tools.preguntar_ia("cómo corro las pruebas")

    assert "#" not in resultado
    assert "`" not in resultado
    assert "pytest" in resultado


def test_preguntar_ia_sin_clave_ni_siquiera_llama_a_gemini(monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    llamadas = []
    monkeypatch.setattr(
        ia_tools.gemini_client,
        "generar",
        lambda pregunta, instruccion_sistema=None: llamadas.append(pregunta),
    )

    resultado = ia_tools.preguntar_ia("lo que sea")

    assert llamadas == []
    assert "clave de Gemini" in resultado


def test_preguntar_ia_avisa_si_no_hay_internet(monkeypatch):
    _falla_con(monkeypatch, requests.ConnectionError("sin red"))

    assert "internet" in ia_tools.preguntar_ia("algo")


def test_preguntar_ia_avisa_si_gemini_tarda_demasiado(monkeypatch):
    _falla_con(monkeypatch, requests.Timeout("muy lento"))

    assert "tardó" in ia_tools.preguntar_ia("algo")


def test_preguntar_ia_explica_el_404_como_problema_del_modelo(monkeypatch):
    _falla_con(
        monkeypatch, requests.HTTPError("404", response=_RespuestaHttp(404))
    )

    assert "modelo" in ia_tools.preguntar_ia("algo")


def test_preguntar_ia_explica_el_403_como_problema_de_la_clave(monkeypatch):
    _falla_con(
        monkeypatch, requests.HTTPError("403", response=_RespuestaHttp(403))
    )

    assert "clave" in ia_tools.preguntar_ia("algo")


def test_preguntar_ia_explica_el_429_como_cuota_agotada(monkeypatch):
    _falla_con(
        monkeypatch, requests.HTTPError("429", response=_RespuestaHttp(429))
    )

    assert "cuota" in ia_tools.preguntar_ia("algo")


def test_preguntar_ia_explica_el_503_sin_culpar_a_la_clave(monkeypatch):
    # Esto pasó de verdad al probar la Fase 6.5: los servidores de Gemini
    # estaban saturados. Un mensaje genérico habría mandado a Javier a revisar
    # su clave de API cuando no había nada que revisar.
    _falla_con(
        monkeypatch, requests.HTTPError("503", response=_RespuestaHttp(503))
    )

    resultado = ia_tools.preguntar_ia("algo")

    assert "saturado" in resultado
    assert "clave" not in resultado


def test_preguntar_ia_con_un_codigo_desconocido_dice_el_numero(monkeypatch):
    _falla_con(
        monkeypatch, requests.HTTPError("418", response=_RespuestaHttp(418))
    )

    assert "418" in ia_tools.preguntar_ia("algo")


def test_preguntar_ia_no_repite_la_url_en_los_errores(monkeypatch):
    # Jarvis lee sus respuestas en voz alta: el texto crudo de un HTTPError
    # trae la URL completa, y dictada letra por letra suena a puro ruido.
    _falla_con(
        monkeypatch,
        requests.HTTPError(
            "404 Client Error: Not Found for url: "
            "https://generativelanguage.googleapis.com/v1beta/models/x:generateContent",
            response=_RespuestaHttp(404),
        ),
    )

    assert "https" not in ia_tools.preguntar_ia("algo")


def test_preguntar_ia_avisa_si_gemini_no_devolvio_texto(monkeypatch):
    _falla_con(monkeypatch, ValueError("Gemini no devolvió ninguna respuesta."))

    assert ia_tools.preguntar_ia("algo") == "Gemini no devolvió ninguna respuesta."


def test_preguntar_ia_nunca_deja_escapar_una_excepcion(monkeypatch):
    # executor.execute() no tiene try/except: si esta herramienta lanzara,
    # se caería todo el programa en vez de contestar.
    for excepcion in (
        requests.ConnectionError("x"),
        requests.Timeout("x"),
        requests.HTTPError("x"),
        requests.TooManyRedirects("x"),
        ValueError("x"),
    ):
        _falla_con(monkeypatch, excepcion)

        assert isinstance(ia_tools.preguntar_ia("algo"), str)
