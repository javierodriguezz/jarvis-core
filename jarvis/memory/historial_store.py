"""
Historial de conversacion.

Fase 4: guarda cada turno (lo que escribio el usuario y lo que le
contesto Jarvis) en la tabla 'historial' de SQLite (data/jarvis.db, ver
jarvis/memory/db.py). A diferencia de jarvis/utils/logger.py (que solo
registra ejecuciones de herramientas para depuracion/auditoria), aqui
queda TODA la interaccion -- incluyendo "no entendi esa instruccion" o
un error de conexion con Ollama -- para que mas adelante el asistente
pueda usarlo como contexto de la conversacion.

Es un registro de solo agregar: no hay funciones para editar o borrar un
turno individual, igual que no editarias una linea ya escrita de un chat.
"""

from datetime import datetime

from jarvis.memory import db


def agregar_turno(texto_usuario: str, respuesta: str) -> dict:
    """Guarda un turno de la conversacion (entrada del usuario + respuesta de Jarvis) y lo regresa."""
    fecha = datetime.now().isoformat(timespec="seconds")
    db.init_db()
    conexion = db.get_connection()
    conexion.execute(
        "INSERT INTO historial (texto_usuario, respuesta, fecha) VALUES (?, ?, ?)",
        (texto_usuario, respuesta, fecha),
    )
    conexion.commit()
    conexion.close()
    return {"texto_usuario": texto_usuario, "respuesta": respuesta, "fecha": fecha}


def listar_historial() -> list[dict]:
    """Regresa todos los turnos guardados, en el orden en que ocurrieron."""
    db.init_db()
    conexion = db.get_connection()
    filas = conexion.execute(
        "SELECT texto_usuario, respuesta, fecha FROM historial ORDER BY id"
    ).fetchall()
    conexion.close()
    return [
        {"texto_usuario": texto_usuario, "respuesta": respuesta, "fecha": fecha}
        for texto_usuario, respuesta, fecha in filas
    ]
