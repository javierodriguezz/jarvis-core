# Proyecto Jarvis

Asistente personal local, inspirado en Jarvis (Iron Man), desarrollado como proyecto de aprendizaje en Python: IA, bases de datos, APIs, seguridad y manejo del sistema operativo.

Ver el plan completo, la arquitectura y el roadmap por fases en [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Estado actual

Fase 1, Fase 2 y Fase 3 completas: asistente de consola cuyo intérprete usa un modelo de lenguaje local (Ollama + `llama3.2`) para decidir qué herramienta llamar, las 5 herramientas iniciales, y confirmación antes de acciones destructivas.

Herramientas `SAFE` (se ejecutan sin preguntar):

- Decir la hora y la fecha.
- Abrir programas o páginas web (lista blanca en `config.py`).
- Crear y consultar notas (guardadas en `data/notes.json`).
- Buscar archivos en carpetas permitidas (`config.ALLOWED_SEARCH_DIRS`).
- Responder preguntas sencillas: predefinidas o cálculos aritméticos simples.

Herramientas `CONFIRM` (piden confirmación s/n antes de ejecutarse):

- Borrar una nota guardada.
- Sobrescribir el texto de una nota existente.

Siguiente paso: Fase 4 (memoria persistente con SQLite). Ver el detalle en [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Cómo correrlo

Requiere [Ollama](https://ollama.com) instalado y corriendo, con el modelo `llama3.2` descargado (`ollama pull llama3.2`).

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
