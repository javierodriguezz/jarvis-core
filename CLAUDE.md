# Proyecto Jarvis

Asistente personal local (estilo Jarvis de Iron Man) desarrollado en Python como proyecto de aprendizaje. Ver `docs/ROADMAP.md` para la arquitectura completa y el plan de trabajo por fases.

## Sobre quién programa esto

Javier es estudiante de 4to semestre de Ingeniería (CUCEI). Tiene base sólida en C/C++ pero está aprendiendo Python. El objetivo del proyecto es tanto tener un asistente funcional como aprender programación, IA, bases de datos, APIs, seguridad y manejo del sistema operativo en el proceso.

## Cómo trabajar en este proyecto (muy importante)

- No entregues código terminado de golpe. Avanza en pasos pequeños: explica qué se va a construir y por qué, escribe una pieza pequeña, pruébala, y confirma que se entendió antes de seguir con la siguiente.
- Explica conceptos nuevos (por ejemplo: entornos virtuales, decoradores, SQLite, async, etc.) al nivel de alguien que viene de C/C++ y apenas está aprendiendo Python — no asumas conocimiento previo de Python específico.
- Cada herramienta o módulo nuevo debe tener al menos una prueba en `tests/` antes de darse por terminado.
- Sigue el roadmap de `docs/ROADMAP.md`. Si una tarea no corresponde a la fase actual, dilo antes de implementarla.

## Reglas de seguridad (no negociables)

- El asistente NUNCA debe tener acceso libre a CMD, PowerShell o ejecutar comandos de shell arbitrarios sobre entrada del usuario (nada de `os.system`/`subprocess` con `shell=True` sobre texto libre).
- Toda acción que el asistente puede ejecutar debe estar registrada explícitamente en `jarvis/tools/registry.py` (lista blanca). No se agregan herramientas "de paso" fuera de ese registro.
- Las herramientas marcadas `CONFIRM` (borrar, enviar, modificar algo importante) deben pedir confirmación explícita antes de ejecutarse. Nunca se quita esa confirmación para "simplificar".
- Las búsquedas de archivos solo deben tocar las carpetas listadas en `config.py -> ALLOWED_SEARCH_DIRS`, nunca el disco completo.

## Estructura

```
main.py                  # Punto de entrada (loop de consola)
config.py                # Configuración y rutas permitidas
jarvis/core/              # interpreter.py (texto -> herramienta), executor.py (valida y ejecuta)
jarvis/tools/              # registry.py (lista blanca) + basic_tools.py (las herramientas en sí)
jarvis/memory/             # notes_store.py (JSON ahora, SQLite en Fase 4)
jarvis/utils/logger.py     # Logging de cada acción ejecutada
tests/                    # Una prueba por herramienta como mínimo
docs/ROADMAP.md            # Plan de trabajo completo por fases
```

## Comandos

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py                # correr el asistente
pytest                        # correr las pruebas
```

## Convenciones

- Nombres de funciones/variables y docstrings en español, para mantener consistencia con el código ya escrito.
- Cada función pública lleva docstring explicando qué hace (útil ahora para Javier y más adelante para que el LLM de la Fase 3 sepa cuándo usar cada herramienta).
