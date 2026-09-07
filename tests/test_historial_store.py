"""
Pruebas del historial de conversacion (jarvis/memory/historial_store.py).
"""

from jarvis.memory import db, historial_store


def _usar_db_temporal(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_FILE", tmp_path / "jarvis.db")


def test_listar_historial_vacio_si_no_hay_turnos(tmp_path, monkeypatch):
    _usar_db_temporal(tmp_path, monkeypatch)

    assert historial_store.listar_historial() == []


def test_agregar_turno_y_listar_historial_redondo(tmp_path, monkeypatch):
    _usar_db_temporal(tmp_path, monkeypatch)

    historial_store.agregar_turno("qué hora es", "Son las 10:00.")
    turnos = historial_store.listar_historial()

    assert len(turnos) == 1
    assert turnos[0]["texto_usuario"] == "qué hora es"
    assert turnos[0]["respuesta"] == "Son las 10:00."
    assert "fecha" in turnos[0]


def test_agregar_turno_conserva_el_orden(tmp_path, monkeypatch):
    _usar_db_temporal(tmp_path, monkeypatch)

    historial_store.agregar_turno("primero", "respuesta 1")
    historial_store.agregar_turno("segundo", "respuesta 2")

    textos = [t["texto_usuario"] for t in historial_store.listar_historial()]
    assert textos == ["primero", "segundo"]


def test_agregar_turno_guarda_instrucciones_no_entendidas(tmp_path, monkeypatch):
    # A diferencia del log de ejecuciones, el historial tambien debe guardar
    # los turnos donde Jarvis no reconocio ninguna herramienta.
    _usar_db_temporal(tmp_path, monkeypatch)

    historial_store.agregar_turno("cuéntame un chiste", "No entendí esa instrucción.")

    turnos = historial_store.listar_historial()
    assert turnos[0]["respuesta"] == "No entendí esa instrucción."
