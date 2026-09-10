# Proyecto Jarvis

Asistente personal local, inspirado en Jarvis (Iron Man), desarrollado como proyecto de aprendizaje en Python: IA, bases de datos, APIs, seguridad y manejo del sistema operativo.

Ver el plan completo, la arquitectura y el roadmap por fases en [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Estado actual

Fase 1 a Fase 5 completas: asistente de consola cuyo intérprete usa un modelo de lenguaje local (Ollama + `llama3.2`) para decidir qué herramienta llamar, las 5 herramientas iniciales, confirmación antes de acciones destructivas, memoria persistente en SQLite (`data/jarvis.db`), y entrada de voz (comando `voz`: graba del micrófono y transcribe con `faster-whisper` antes de mandarlo al mismo intérprete).

Herramientas `SAFE` (se ejecutan sin preguntar):

- Decir la hora y la fecha.
- Abrir programas o páginas web (lista blanca en `config.py`).
- Crear y consultar notas (guardadas en SQLite, tabla `notas`).
- Buscar archivos en carpetas permitidas (`config.ALLOWED_SEARCH_DIRS`).
- Responder preguntas sencillas: predefinidas o cálculos aritméticos simples.

Herramientas `CONFIRM` (piden confirmación s/n antes de ejecutarse):

- Borrar una nota guardada.
- Sobrescribir el texto de una nota existente.

Cada turno de la conversación (incluyendo "no entendí" o errores de conexión con Ollama) queda guardado en la tabla `historial` de SQLite. La tabla de preferencias del usuario, contemplada en la Fase 4 original, se dejó pendiente hasta que exista una herramienta real que la necesite.

Siguiente paso: Fase 6 (salida de voz, con Piper). Ver el detalle en [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Cómo correrlo

Requiere [Ollama](https://ollama.com) instalado y corriendo, con el modelo `llama3.2` descargado (`ollama pull llama3.2`), y un micrófono conectado si vas a usar el comando `voz`.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
chcp 65001
python main.py
```

`chcp 65001` cambia el codepage de la consola de Windows a UTF-8; sin eso, los acentos pueden mostrarse como caracteres rotos.

Escribe `voz` en vez de una instrucción para grabar unos segundos del micrófono y transcribirlos con Whisper (modelo local, sin mandar audio a ningún servicio externo); el texto transcrito entra al mismo intérprete que si lo hubieras escrito a mano. La primera vez que se usa, `faster-whisper` descarga el modelo configurado en `WHISPER_MODEL` (`.env`, por defecto `base`) y lo deja cacheado en disco.

## Cómo correr las pruebas

```bash
pytest
```

## Principios de seguridad

- El asistente **no tiene acceso libre a CMD, PowerShell ni la terminal**.
- Solo puede ejecutar herramientas explícitamente registradas en `jarvis/tools/registry.py`.
- Las acciones delicadas (borrar, modificar, enviar) piden confirmación antes de ejecutarse.
