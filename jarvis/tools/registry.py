"""
Registro de herramientas: la lista blanca completa de lo que Jarvis puede hacer.

Cada herramienta se registra explícitamente con:
  - name: nombre único que usa el intérprete para referirse a ella.
  - func: la función de Python que efectivamente hace el trabajo.
  - permission: "SAFE" (se ejecuta sin preguntar) o "CONFIRM" (pide confirmación).
  - description: para que el LLM (Fase 3) sepa cuándo usarla.

Nada que no esté en TOOLS puede ejecutarse. Este archivo es, a propósito,
el único lugar donde se decide qué puede hacer el asistente en el sistema.
"""

from jarvis.tools import basic_tools

TOOLS = {
    "decir_hora": {
        "func": basic_tools.decir_hora,
        "permission": "SAFE",
        "description": "Dice la hora y fecha actuales.",
    },
}
