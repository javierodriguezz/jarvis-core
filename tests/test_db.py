"""
Pruebas de la conexion a la base de datos (jarvis/memory/db.py).
"""

from jarvis.memory import db


def test_init_db_crea_la_tabla_notas(tmp_path, monkeypatch):
    # Igual que en test_notes_store.py: redirigimos el archivo a una carpeta
    # temporal para no tocar el data/jarvis.db real durante las pruebas.
    monkeypatch.setattr(db, "DB_FILE", tmp_path / "jarvis.db")

    db.init_db()

    conexion = db.get_connection()
    columnas = conexion.execute("PRAGMA table_info(notas)").fetchall()
    conexion.close()

    # Cada fila de PRAGMA table_info es (cid, nombre, tipo, notnull, default, pk).
    nombres_columnas = [fila[1] for fila in columnas]
    assert nombres_columnas == ["id", "texto", "creada", "editada"]


def test_init_db_crea_la_tabla_historial(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_FILE", tmp_path / "jarvis.db")

    db.init_db()

    conexion = db.get_connection()
    columnas = conexion.execute("PRAGMA table_info(historial)").fetchall()
    conexion.close()

    nombres_columnas = [fila[1] for fila in columnas]
    assert nombres_columnas == ["id", "texto_usuario", "respuesta", "fecha"]


def test_init_db_es_seguro_llamarlo_dos_veces(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_FILE", tmp_path / "jarvis.db")

    db.init_db()
    db.init_db()  # no debe lanzar error ni duplicar las tablas

    conexion = db.get_connection()
    tablas = conexion.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('notas', 'historial')"
    ).fetchall()
    conexion.close()

    assert len(tablas) == 2
