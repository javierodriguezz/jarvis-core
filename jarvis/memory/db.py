"""
Conexion a la base de datos SQLite del proyecto (Fase 4).

SQLite no es un proceso servidor aparte -- es un solo archivo
(data/jarvis.db) que Python lee y escribe directamente a traves del
modulo sqlite3, incluido en la libreria estandar (no hay que instalar
nada extra).
"""

import sqlite3

from config import DATA_DIR

DB_FILE = DATA_DIR / "jarvis.db"


def get_connection() -> sqlite3.Connection:
    """Abre (creando el archivo si todavia no existe) y regresa la conexion a data/jarvis.db.

    Quien llama esta funcion es responsable de cerrar la conexion despues
    (o usarla dentro de un 'with').
    """
    DATA_DIR.mkdir(exist_ok=True)
    return sqlite3.connect(DB_FILE)


def init_db() -> None:
    """Crea las tablas del proyecto si todavia no existen ('notas', 'historial').

    Es seguro llamar esta funcion varias veces (por ejemplo, una vez por
    cada arranque de main.py): CREATE TABLE IF NOT EXISTS no hace nada si
    la tabla ya esta creada de una corrida anterior.
    """
    conexion = get_connection()
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT NOT NULL,
            creada TEXT NOT NULL,
            editada TEXT
        )
        """
    )
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto_usuario TEXT NOT NULL,
            respuesta TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
        """
    )
    conexion.commit()
    conexion.close()
