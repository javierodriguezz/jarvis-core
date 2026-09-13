"""
Pruebas del registro de herramientas (lista blanca).

Verifican que cada herramienta registrada tenga la forma esperada -- esto
importa porque executor.py va a confiar ciegamente en esa forma (func,
permission, description) para decidir qué y cómo ejecutar.
"""

from jarvis.tools.registry import TOOLS

PERMISOS_VALIDOS = {"SAFE", "CONFIRM"}


def test_decir_hora_registrada():
    assert "decir_hora" in TOOLS


def test_decir_hora_tiene_forma_correcta():
    entrada = TOOLS["decir_hora"]

    assert callable(entrada["func"])
    assert entrada["permission"] in PERMISOS_VALIDOS
    assert isinstance(entrada["description"], str) and entrada["description"]


def test_decir_hora_es_safe():
    assert TOOLS["decir_hora"]["permission"] == "SAFE"


def test_abrir_programa_o_web_registrada():
    assert "abrir_programa_o_web" in TOOLS


def test_abrir_programa_o_web_tiene_forma_correcta():
    entrada = TOOLS["abrir_programa_o_web"]

    assert callable(entrada["func"])
    assert entrada["permission"] in PERMISOS_VALIDOS
    assert isinstance(entrada["description"], str) and entrada["description"]


def test_notas_registradas_y_con_forma_correcta():
    for nombre in ("crear_nota", "consultar_notas"):
        entrada = TOOLS[nombre]

        assert callable(entrada["func"])
        assert entrada["permission"] in PERMISOS_VALIDOS
        assert isinstance(entrada["description"], str) and entrada["description"]


def test_borrar_nota_registrada_y_es_confirm():
    entrada = TOOLS["borrar_nota"]

    assert callable(entrada["func"])
    assert entrada["permission"] == "CONFIRM"
    assert isinstance(entrada["description"], str) and entrada["description"]


def test_sobrescribir_nota_registrada_y_es_confirm():
    entrada = TOOLS["sobrescribir_nota"]

    assert callable(entrada["func"])
    assert entrada["permission"] == "CONFIRM"
    assert isinstance(entrada["description"], str) and entrada["description"]


def test_buscar_archivos_registrada_y_con_forma_correcta():
    entrada = TOOLS["buscar_archivos"]

    assert callable(entrada["func"])
    assert entrada["permission"] in PERMISOS_VALIDOS
    assert isinstance(entrada["description"], str) and entrada["description"]


def test_responder_pregunta_registrada_y_con_forma_correcta():
    entrada = TOOLS["responder_pregunta"]

    assert callable(entrada["func"])
    assert entrada["permission"] in PERMISOS_VALIDOS
    assert isinstance(entrada["description"], str) and entrada["description"]


def test_preguntar_ia_registrada():
    assert "preguntar_ia" in TOOLS


def test_preguntar_ia_tiene_forma_correcta():
    entrada = TOOLS["preguntar_ia"]

    assert callable(entrada["func"])
    assert entrada["permission"] in PERMISOS_VALIDOS
    assert isinstance(entrada["description"], str) and entrada["description"]


def test_preguntar_ia_es_safe():
    # No modifica ni borra nada, así que no pide confirmación. Lo que sí hace,
    # y ninguna otra herramienta hace, es mandar texto del usuario a un
    # servicio externo -- por eso su description lo dice explícitamente.
    assert TOOLS["preguntar_ia"]["permission"] == "SAFE"
