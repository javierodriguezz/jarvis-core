"""
Pruebas del intérprete (jarvis/core/interpreter.py).

Desde la Fase 3, interpret() habla con Ollama a través de llm_client.generar.
Estas pruebas nunca llaman al Ollama real: reemplazan llm_client.generar por
una versión falsa que regresa un texto fijo, y verifican que interpret()
sepa convertir (o rechazar) esa respuesta correctamente. Así las pruebas
corren rápido y no dependen de que el servicio esté encendido.
"""

import json

import pytest
import requests

from jarvis.core import interpreter
from jarvis.core.interpreter import ToolCall, interpret


def _responder_con(monkeypatch, texto: str):
    """Hace que llm_client.generar() regrese 'texto' sin llamar a Ollama de verdad."""
    monkeypatch.setattr(interpreter.llm_client, "generar", lambda _prompt: texto)


def test_reconoce_herramienta_sin_parametros(monkeypatch):
    _responder_con(monkeypatch, '{"tool_name": "decir_hora", "params": {}}')

    resultado = interpret("qué hora es")

    assert resultado == ToolCall(tool_name="decir_hora", params={})


def test_reconoce_herramienta_con_parametros(monkeypatch):
    _responder_con(
        monkeypatch,
        '{"tool_name": "abrir_programa_o_web", "params": {"nombre": "youtube"}}',
    )

    resultado = interpret("abre youtube")

    assert resultado == ToolCall(
        tool_name="abrir_programa_o_web", params={"nombre": "youtube"}
    )


def test_tool_name_null_devuelve_none(monkeypatch):
    _responder_con(monkeypatch, '{"tool_name": null, "params": {}}')

    assert interpret("cuéntame un chiste") is None


def test_json_invalido_devuelve_none(monkeypatch):
    _responder_con(monkeypatch, "esto no es JSON para nada")

    assert interpret("algo") is None


def test_herramienta_inventada_no_existe_devuelve_none(monkeypatch):
    # El modelo puede alucinar un nombre de herramienta que no está en el
    # registro -- interpret() nunca debe confiar en eso a ciegas.
    _responder_con(monkeypatch, '{"tool_name": "formatear_disco", "params": {}}')

    assert interpret("borra todo") is None


def test_parametros_de_mas_devuelve_none(monkeypatch):
    _responder_con(
        monkeypatch,
        '{"tool_name": "decir_hora", "params": {"zona_horaria": "CDMX"}}',
    )

    assert interpret("qué hora es") is None


def test_parametros_faltantes_devuelve_none(monkeypatch):
    _responder_con(
        monkeypatch, '{"tool_name": "abrir_programa_o_web", "params": {}}'
    )

    assert interpret("abre algo") is None


def test_extrae_json_aunque_venga_con_texto_alrededor(monkeypatch):
    _responder_con(
        monkeypatch,
        'Claro, aquí está: {"tool_name": "decir_hora", "params": {}} espero que ayude.',
    )

    resultado = interpret("qué hora es")

    assert resultado == ToolCall(tool_name="decir_hora", params={})


def test_propaga_error_de_conexion_con_ollama(monkeypatch):
    def generar_que_falla(_prompt):
        raise requests.ConnectionError("Ollama no está corriendo")

    monkeypatch.setattr(interpreter.llm_client, "generar", generar_que_falla)

    with pytest.raises(requests.ConnectionError):
        interpret("qué hora es")


def test_prompt_incluye_la_instruccion_del_usuario(monkeypatch):
    prompts_recibidos = []

    def generar_falso(prompt):
        prompts_recibidos.append(prompt)
        return '{"tool_name": "decir_hora", "params": {}}'

    monkeypatch.setattr(interpreter.llm_client, "generar", generar_falso)

    interpret("qué hora es en este momento")

    assert "qué hora es en este momento" in prompts_recibidos[0]
    assert "decir_hora" in prompts_recibidos[0]


def test_describir_herramientas_incluye_todas_las_registradas():
    from jarvis.tools.registry import TOOLS

    descripcion = interpreter._describir_herramientas()

    for nombre in TOOLS:
        assert nombre in descripcion


def test_extraer_bloque_json_sin_llaves_devuelve_none():
    assert interpreter._extraer_bloque_json("sin json aquí") is None
