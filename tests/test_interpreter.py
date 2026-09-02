"""
Pruebas del intérprete (jarvis/core/interpreter.py).
"""

from jarvis.core.interpreter import ToolCall, interpret


def test_reconoce_pregunta_por_la_hora():
    resultado = interpret("¿qué hora es?")

    assert resultado == ToolCall(tool_name="decir_hora", params={})


def test_reconoce_pregunta_por_la_fecha():
    resultado = interpret("dime la fecha de hoy")

    assert resultado == ToolCall(tool_name="decir_hora", params={})


def test_no_distingue_mayusculas():
    resultado = interpret("QUÉ HORA ES")

    assert resultado == ToolCall(tool_name="decir_hora", params={})


def test_texto_no_reconocido_devuelve_none():
    resultado = interpret("cuéntame un chiste")

    assert resultado is None


def test_reconoce_abrir_programa_o_web():
    resultado = interpret("abre youtube")

    assert resultado == ToolCall(
        tool_name="abrir_programa_o_web", params={"nombre": "youtube"}
    )


def test_reconoce_abrir_con_variante_infinitivo():
    resultado = interpret("quiero abrir github")

    assert resultado == ToolCall(
        tool_name="abrir_programa_o_web", params={"nombre": "github"}
    )
