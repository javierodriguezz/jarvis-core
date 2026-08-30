"""
Pruebas del ejecutor (jarvis/core/executor.py).
"""

from jarvis.core.executor import execute
from jarvis.core.interpreter import ToolCall
from jarvis.tools import registry


def test_execute_herramienta_valida_devuelve_resultado():
    resultado = execute(ToolCall(tool_name="decir_hora", params={}))

    assert "Son las" in resultado


def test_execute_herramienta_desconocida_no_truena():
    resultado = execute(ToolCall(tool_name="volar", params={}))

    assert "volar" in resultado


def test_execute_pide_confirmacion_y_respeta_no(monkeypatch):
    llamada_hecha = []
    registry.TOOLS["prueba_confirm"] = {
        "func": lambda: llamada_hecha.append(True),
        "permission": "CONFIRM",
        "description": "Herramienta falsa solo para esta prueba.",
    }
    monkeypatch.setattr("builtins.input", lambda _: "n")

    resultado = execute(ToolCall(tool_name="prueba_confirm", params={}))

    assert "Cancelado" in resultado
    assert llamada_hecha == []
    del registry.TOOLS["prueba_confirm"]


def test_execute_pide_confirmacion_y_respeta_si(monkeypatch):
    llamada_hecha = []
    registry.TOOLS["prueba_confirm"] = {
        "func": lambda: llamada_hecha.append(True) or "hecho",
        "permission": "CONFIRM",
        "description": "Herramienta falsa solo para esta prueba.",
    }
    monkeypatch.setattr("builtins.input", lambda _: "s")

    resultado = execute(ToolCall(tool_name="prueba_confirm", params={}))

    assert resultado == "hecho"
    assert llamada_hecha == [True]
    del registry.TOOLS["prueba_confirm"]
