"""
Pruebas del ejecutor (jarvis/core/executor.py).
"""

from jarvis.core import interpreter
from jarvis.core.executor import execute
from jarvis.core.interpreter import ToolCall
from jarvis.memory import notes_store
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


# Pruebas de punta a punta: interpreter.interpret() + executor.execute() juntos,
# igual que los usa main.py -- confirman que el flujo completo de Fase 2
# (texto del usuario -> ToolCall -> confirmación -> acción real) funciona,
# no solo cada pieza por separado.


def test_flujo_completo_borrar_nota_cancelada_no_borra(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")
    notes_store.add_note("comprar pan")
    monkeypatch.setattr("builtins.input", lambda _: "n")

    tool_call = interpreter.interpret("borra la nota 1")
    resultado = execute(tool_call)

    assert "Cancelado" in resultado
    assert notes_store.list_notes()[0]["texto"] == "comprar pan"


def test_flujo_completo_borrar_nota_confirmada_borra(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")
    notes_store.add_note("comprar pan")
    monkeypatch.setattr("builtins.input", lambda _: "s")

    tool_call = interpreter.interpret("borra la nota 1")
    resultado = execute(tool_call)

    assert "comprar pan" in resultado
    assert notes_store.list_notes() == []


def test_flujo_completo_sobrescribir_nota_confirmada_actualiza(tmp_path, monkeypatch):
    monkeypatch.setattr(notes_store, "NOTES_FILE", tmp_path / "notes.json")
    notes_store.add_note("comprar pan")
    monkeypatch.setattr("builtins.input", lambda _: "s")

    tool_call = interpreter.interpret("sobrescribe la nota 1 con comprar leche")
    resultado = execute(tool_call)

    assert "comprar leche" in resultado
    assert notes_store.list_notes()[0]["texto"] == "comprar leche"
