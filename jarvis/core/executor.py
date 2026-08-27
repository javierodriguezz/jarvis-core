"""
Ejecutor: la capa de seguridad entre el intérprete y las herramientas.

Reglas que este módulo debe garantizar SIEMPRE (ver docs/ROADMAP.md, sección 1):
  1. Solo se ejecutan herramientas que existan en el registro (jarvis/tools/registry.py).
  2. Si la herramienta requiere confirmación, se pide antes de ejecutar.
  3. Toda ejecución (exitosa o no) queda registrada en el log.

TODO (Fase 1): implementar execute() usando el registro de herramientas.
"""


def execute(tool_call) -> str:
    raise NotImplementedError("Lo implementamos junto con el registro de herramientas.")
