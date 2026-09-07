"""
Almacenamiento de notas.

Fase 4: la tabla 'notas' de SQLite (data/jarvis.db, ver jarvis/memory/db.py)
reemplaza al JSON de las fases anteriores.

La interfaz publica (las funciones que expone este modulo) se mantiene
igual que en la Fase 1 -- el resto del sistema (basic_tools.py) no nota
el cambio de JSON a SQLite. La numeracion visible de las notas (1, 2, 3...
la que ve el usuario) tampoco cambia: sigue siendo la posicion en el orden
de creacion. Por dentro, cada nota ahora tambien tiene un 'id' propio en
SQLite que nunca cambia, aunque se borren otras notas -- por eso cada
dict que regresan estas funciones incluye ese 'id'.
"""

from datetime import datetime

from jarvis.memory import db


def _conexion():
    """Se asegura de que la tabla 'notas' exista y regresa una conexion lista para usar."""
    db.init_db()
    return db.get_connection()


def _fila_a_nota(fila) -> dict:
    """Convierte una fila (id, texto, creada, editada) en el dict que espera el resto del sistema."""
    id_, texto, creada, editada = fila
    nota = {"id": id_, "texto": texto, "creada": creada}
    if editada is not None:
        nota["editada"] = editada
    return nota


def _id_por_indice(conexion, indice: int) -> int | None:
    """Traduce el numero visible (1-based, el que ve el usuario) al id interno de esa fila.

    Regresa None si el indice es menor a 1 o no corresponde a ninguna nota.
    """
    if indice < 1:
        return None
    fila = conexion.execute(
        "SELECT id FROM notas ORDER BY id LIMIT 1 OFFSET ?", (indice - 1,)
    ).fetchone()
    return fila[0] if fila else None


def add_note(texto: str) -> dict:
    """Agrega una nota nueva a la tabla 'notas' y la regresa (incluyendo su id)."""
    creada = datetime.now().isoformat(timespec="seconds")
    conexion = _conexion()
    cursor = conexion.execute(
        "INSERT INTO notas (texto, creada) VALUES (?, ?)", (texto, creada)
    )
    conexion.commit()
    nuevo_id = cursor.lastrowid
    conexion.close()
    return {"id": nuevo_id, "texto": texto, "creada": creada}


def list_notes() -> list[dict]:
    """Regresa todas las notas guardadas, en el orden en que se crearon."""
    conexion = _conexion()
    filas = conexion.execute(
        "SELECT id, texto, creada, editada FROM notas ORDER BY id"
    ).fetchall()
    conexion.close()
    return [_fila_a_nota(fila) for fila in filas]


def delete_note(indice: int) -> dict | None:
    """Borra la nota en la posicion 'indice' (1-based, como se ve en list_notes).

    Regresa la nota borrada, o None si el indice no corresponde a ninguna
    nota -- asi basic_tools.borrar_nota puede distinguir "borre algo" de
    "ese numero no existe" sin necesidad de excepciones.
    """
    conexion = _conexion()
    id_ = _id_por_indice(conexion, indice)
    if id_ is None:
        conexion.close()
        return None

    fila = conexion.execute(
        "SELECT id, texto, creada, editada FROM notas WHERE id = ?", (id_,)
    ).fetchone()
    nota = _fila_a_nota(fila)
    conexion.execute("DELETE FROM notas WHERE id = ?", (id_,))
    conexion.commit()
    conexion.close()
    return nota


def update_note(indice: int, texto_nuevo: str) -> dict | None:
    """Sobrescribe el texto de la nota en la posicion 'indice' (1-based).

    Regresa la nota ya actualizada, o None si el indice no corresponde a
    ninguna nota. Guarda 'editada' con la fecha del cambio, sin tocar
    'creada' -- asi queda rastro de que la nota se modifico.
    """
    conexion = _conexion()
    id_ = _id_por_indice(conexion, indice)
    if id_ is None:
        conexion.close()
        return None

    editada = datetime.now().isoformat(timespec="seconds")
    conexion.execute(
        "UPDATE notas SET texto = ?, editada = ? WHERE id = ?",
        (texto_nuevo, editada, id_),
    )
    conexion.commit()
    fila = conexion.execute(
        "SELECT id, texto, creada, editada FROM notas WHERE id = ?", (id_,)
    ).fetchone()
    conexion.close()
    return _fila_a_nota(fila)
