"""
Intérprete de instrucciones.

Fase 1: reglas simples (palabras clave / regex) que deciden qué herramienta
llamar y con qué parámetros.

Fase 3: esta misma función se reemplaza internamente por una llamada a un
modelo de lenguaje local (Ollama), pero la firma (lo que recibe y lo que
regresa) se mantiene igual -- por eso el resto del sistema no necesita
cambiar cuando lleguemos a esa fase.

TODO (Fase 1, primera sesión de código): implementar interpret() para que
reconozca al menos la instrucción de "qué hora es".
"""

from dataclasses import dataclass


@dataclass
class ToolCall:
    tool_name: str
    params: dict


def interpret(user_text: str) -> ToolCall | None:
    """Traduce texto libre del usuario a una llamada de herramienta.

    Devuelve None si no reconoce ninguna instrucción.
    """
    raise NotImplementedError("Lo implementamos juntos en la Fase 1.")
