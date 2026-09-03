# Proyecto Jarvis

Asistente personal local, inspirado en Jarvis (Iron Man), desarrollado como proyecto de aprendizaje en Python: IA, bases de datos, APIs, seguridad y manejo del sistema operativo.

Ver el plan completo, la arquitectura y el roadmap por fases en [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Estado actual

Fase 1 completa: asistente de consola con intérprete de reglas simples (palabras clave) y las 5 herramientas iniciales:

- Decir la hora y la fecha.
- Abrir programas o páginas web (lista blanca en `config.py`).
- Crear y consultar notas (guardadas en `data/notes.json`).
- Buscar archivos en carpetas permitidas (`config.ALLOWED_SEARCH_DIRS`).
- Responder preguntas sencillas: predefinidas o cálculos aritméticos simples.

Siguiente paso: Fase 2 (arquitectura de permisos y confirmaciones formales). Ver el detalle en [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Cómo correrlo

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
chcp 65001
python main.py
```

`chcp 65001` cambia el codepage de la consola de Windows a UTF-8; sin eso, los acentos pueden mostrarse como caracteres rotos.

## Cómo correr las pruebas

```bash
pytest
```

## Principios de seguridad

- El asistente **no tiene acceso libre a CMD, PowerShell ni la terminal**.
- Solo puede ejecutar herramientas explícitamente registradas en `jarvis/tools/registry.py`.
- Las acciones delicadas (borrar, modificar, enviar) piden confirmación antes de ejecutarse.
