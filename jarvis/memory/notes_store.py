"""
Almacenamiento de notas.

Fase 1: un archivo JSON simple en data/notes.json.
Fase 4: se migra a SQLite (data/jarvis.db) con una tabla notes y,
más adelante, tablas para preferencias e historial de conversación.

La interfaz pública (las funciones que expone este módulo) se mantiene
igual entre ambas fases -- otra vez, el resto del sistema no debería
notar el cambio de JSON a SQLite.
"""

import json
from datetime import datetime

from config import DATA_DIR

NOTES_FILE = DATA_DIR / "notes.json"


def _leer_notas() -> list[dict]:
    """Lee data/notes.json y regresa la lista de notas (vacía si el archivo no existe todavía)."""
    if not NOTES_FILE.exists():
        return []
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _guardar_notas(notas: list[dict]) -> None:
    """Sobrescribe data/notes.json con la lista de notas completa."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notas, f, ensure_ascii=False, indent=2)


def add_note(texto: str) -> dict:
    """Agrega una nota nueva a data/notes.json y la regresa."""
    notas = _leer_notas()
    nota = {"texto": texto, "creada": datetime.now().isoformat(timespec="seconds")}
    notas.append(nota)
    _guardar_notas(notas)
    return nota


def list_notes() -> list[dict]:
    """Regresa todas las notas guardadas, en el orden en que se crearon."""
    return _leer_notas()


def delete_note(indice: int) -> dict | None:
    """Borra la nota en la posición 'indice' (1-based, como se ve en list_notes).

    Regresa la nota borrada, o None si el índice no corresponde a ninguna
    nota -- así basic_tools.borrar_nota puede distinguir "borré algo" de
    "ese número no existe" sin necesidad de excepciones.
    """
    notas = _leer_notas()
    posicion = indice - 1
    if posicion < 0 or posicion >= len(notas):
        return None

    nota = notas.pop(posicion)
    _guardar_notas(notas)
    return nota


def update_note(indice: int, texto_nuevo: str) -> dict | None:
    """Sobrescribe el texto de la nota en la posición 'indice' (1-based).

    Regresa la nota ya actualizada, o None si el índice no corresponde a
    ninguna nota. Guarda un campo 'editada' con la fecha del cambio, sin
    tocar 'creada' -- así queda rastro de que la nota se modificó.
    """
    notas = _leer_notas()
    posicion = indice - 1
    if posicion < 0 or posicion >= len(notas):
        return None

    notas[posicion]["texto"] = texto_nuevo
    notas[posicion]["editada"] = datetime.now().isoformat(timespec="seconds")
    _guardar_notas(notas)
    return notas[posicion]
