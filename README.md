# Proyecto Jarvis

Asistente personal local, inspirado en Jarvis (Iron Man), desarrollado como proyecto de aprendizaje en Python: IA, bases de datos, APIs, seguridad y manejo del sistema operativo.

Ver el plan completo, la arquitectura y el roadmap por fases en [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Estado actual

Fase 1 a Fase 6.5 completas: asistente de consola cuyo intérprete usa un modelo de lenguaje local (Ollama + `llama3.2`) para decidir qué herramienta llamar, las 5 herramientas iniciales, confirmación antes de acciones destructivas, memoria persistente en SQLite (`data/jarvis.db`), entrada de voz (comando `voz`: graba del micrófono y transcribe con `faster-whisper`), salida de voz (cada respuesta se reproduce en voz alta con Piper, 100% local) y preguntas abiertas contestadas por una IA en la nube (Gemini) cuando ninguna herramienta local aplica.

Herramientas `SAFE` (se ejecutan sin preguntar):

- Decir la hora y la fecha.
- Abrir programas o páginas web (lista blanca en `config.py`).
- Crear y consultar notas (guardadas en SQLite, tabla `notas`).
- Buscar archivos en carpetas permitidas (`config.ALLOWED_SEARCH_DIRS`).
- Responder preguntas sencillas: predefinidas o cálculos aritméticos simples.
- Responder preguntas abiertas con una IA en la nube (Gemini). Es la única herramienta que manda texto fuera de la máquina.

Herramientas `CONFIRM` (piden confirmación s/n antes de ejecutarse):

- Borrar una nota guardada.
- Sobrescribir el texto de una nota existente.

Cada turno de la conversación (incluyendo los errores de conexión con Ollama) queda guardado en la tabla `historial` de SQLite. La tabla de preferencias del usuario, contemplada en la Fase 4 original, se dejó pendiente hasta que exista una herramienta real que la necesite.

Siguiente paso: Fase 7 (palabra de activación, con openWakeWord). Ver el detalle en [`docs/ROADMAP.md`](docs/ROADMAP.md).

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

Cada respuesta de Jarvis también se escucha en voz alta, sintetizada con Piper (también 100% local). La voz se elige con `PIPER_VOICE` (`.env`, por defecto `es_ES-davefx-medium`); sus archivos (`.onnx` y `.onnx.json`) se descargan una sola vez a `data/voices/` con `python -m piper.download_voices --download-dir data/voices <nombre-de-voz>` y no se suben a git.

Si una instrucción no corresponde a ninguna herramienta local, Jarvis se la pasa a Gemini en vez de contestar que no entendió. Para eso hace falta una clave de API gratuita de [Google AI Studio](https://aistudio.google.com/apikey), puesta en `GEMINI_API_KEY` dentro de `.env` (ese archivo nunca se sube a git). El modelo se elige con `GEMINI_MODEL`; por defecto `gemini-3.6-flash`, porque los alias tipo `-latest` suelen responder 503 por saturación. Sin clave configurada, todo lo demás sigue funcionando igual y solo esa herramienta avisa que le falta la clave.

## Cómo correr las pruebas

```bash
pytest
```

## Principios de seguridad

- El asistente **no tiene acceso libre a CMD, PowerShell ni la terminal**.
- Solo puede ejecutar herramientas explícitamente registradas en `jarvis/tools/registry.py`.
- Las acciones delicadas (borrar, modificar, enviar) piden confirmación antes de ejecutarse.
