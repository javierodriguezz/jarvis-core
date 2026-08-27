# Proyecto Jarvis

Asistente personal local, inspirado en Jarvis (Iron Man), desarrollado como proyecto de aprendizaje en Python: IA, bases de datos, APIs, seguridad y manejo del sistema operativo.

Ver el plan completo, la arquitectura y el roadmap por fases en [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Estado actual

🚧 Fase 0 — esqueleto inicial. Todavía no hay herramientas implementadas.

## Cómo correrlo (cuando el entorno esté listo)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Principios de seguridad

- El asistente **no tiene acceso libre a CMD, PowerShell ni la terminal**.
- Solo puede ejecutar herramientas explícitamente registradas en `jarvis/tools/registry.py`.
- Las acciones delicadas (borrar, modificar, enviar) piden confirmación antes de ejecutarse.
