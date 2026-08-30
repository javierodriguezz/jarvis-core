"""
Ejecutor: la capa de seguridad entre el intérprete y las herramientas.

Reglas que este módulo debe garantizar SIEMPRE (ver docs/ROADMAP.md, sección 1):
  1. Solo se ejecutan herramientas que existan en el registro (jarvis/tools/registry.py).
  2. Si la herramienta requiere confirmación, se pide antes de ejecutar.
  3. Toda ejecución (exitosa o no) queda registrada en el log.
"""

from jarvis.tools import registry
from jarvis.utils import logger


def execute(tool_call) -> str:
    """Valida y ejecuta una ToolCall contra el registro de herramientas.

    Devuelve siempre un string: el resultado de la herramienta, o un mensaje
    explicando por qué no se ejecutó (no existe / no se confirmó).
    """
    entrada = registry.TOOLS.get(tool_call.tool_name)

    if entrada is None:
        resultado = f"No reconozco la herramienta '{tool_call.tool_name}'."
        logger.registrar_ejecucion(tool_call.tool_name, tool_call.params, resultado)
        return resultado

    if entrada["permission"] == "CONFIRM":
        respuesta = input(f"¿Confirmas ejecutar '{tool_call.tool_name}'? (s/n): ")
        if respuesta.strip().lower() != "s":
            resultado = "Cancelado: no se confirmó la acción."
            logger.registrar_ejecucion(tool_call.tool_name, tool_call.params, resultado)
            return resultado

    resultado = entrada["func"](**tool_call.params)
    logger.registrar_ejecucion(tool_call.tool_name, tool_call.params, resultado)
    return resultado
