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


def test_reconoce_crear_nota_con_anota_que():
    resultado = interpret("anota que hoy es viernes")

    assert resultado == ToolCall(
        tool_name="crear_nota", params={"texto": "hoy es viernes"}
    )


def test_reconoce_crear_nota_con_apunta():
    resultado = interpret("apunta comprar leche")

    assert resultado == ToolCall(
        tool_name="crear_nota", params={"texto": "comprar leche"}
    )


def test_reconoce_consultar_notas():
    resultado = interpret("¿cuáles son mis notas?")

    assert resultado == ToolCall(tool_name="consultar_notas", params={})


def test_reconoce_buscar_archivo():
    resultado = interpret("busca archivo reporte")

    assert resultado == ToolCall(
        tool_name="buscar_archivos", params={"nombre": "reporte"}
    )


def test_reconoce_pregunta_predefinida():
    resultado = interpret("¿Cómo te llamas?")

    assert resultado == ToolCall(
        tool_name="responder_pregunta", params={"pregunta": "¿Cómo te llamas?"}
    )


def test_reconoce_pregunta_de_calculo():
    resultado = interpret("cuánto es 2 + 2")

    assert resultado == ToolCall(
        tool_name="responder_pregunta", params={"pregunta": "cuánto es 2 + 2"}
    )
