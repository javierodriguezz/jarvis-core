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
    "abrir_programa_o_web": {
        "func": basic_tools.abrir_programa_o_web,
        "permission": "SAFE",
        "description": "Abre un programa o página web de la lista blanca.",
    },
    "crear_nota": {
        "func": basic_tools.crear_nota,
        "permission": "SAFE",
        "description": "Guarda una nota de texto nueva.",
    },
    "consultar_notas": {
        "func": basic_tools.consultar_notas,
        "permission": "SAFE",
        "description": "Muestra todas las notas guardadas.",
    },
    "borrar_nota": {
        "func": basic_tools.borrar_nota,
        "permission": "CONFIRM",
        "description": "Borra una nota guardada por su número. Acción destructiva.",
    },
    "sobrescribir_nota": {
        "func": basic_tools.sobrescribir_nota,
        "permission": "CONFIRM",
        "description": "Reemplaza el texto de una nota existente por su número. Acción destructiva.",
    },
    "buscar_archivos": {
        "func": basic_tools.buscar_archivos,
        "permission": "SAFE",
        "description": "Busca archivos por nombre dentro de las carpetas permitidas.",
    },
    "responder_pregunta": {
        "func": basic_tools.responder_pregunta,
        "permission": "SAFE",
        "description": "Responde preguntas sencillas predefinidas o cálculos aritméticos simples.",
    },
}
