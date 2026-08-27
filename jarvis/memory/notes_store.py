"""
Almacenamiento de notas.

Fase 1: un archivo JSON simple en data/notes.json.
Fase 4: se migra a SQLite (data/jarvis.db) con una tabla notes y,
más adelante, tablas para preferencias e historial de conversación.

La interfaz pública (las funciones que expone este módulo) se mantiene
igual entre ambas fases -- otra vez, el resto del sistema no debería
notar el cambio de JSON a SQLite.

TODO (Fase 1): implementar add_note() y list_notes() sobre JSON.
"""
