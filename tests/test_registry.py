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


def test_buscar_archivos_registrada_y_con_forma_correcta():
    entrada = TOOLS["buscar_archivos"]

    assert callable(entrada["func"])
    assert entrada["permission"] in PERMISOS_VALIDOS
    assert isinstance(entrada["description"], str) and entrada["description"]
