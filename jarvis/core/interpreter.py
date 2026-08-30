"""
Intérprete de instrucciones.

Fase 1: reglas simples (palabras clave / regex) que deciden qué herramienta
llamar y con qué parámetros.

Fase 3: esta misma función se reemplaza internamente por una llamada a un
modelo de lenguaje local (Ollama), pero la firma (lo que recibe y lo que
regresa) se mantiene igual -- por eso el resto del sistema no necesita
cambiar cuando lleguemos a esa fase.
"""

from dataclasses import dataclass


@dataclass
class ToolCall:
    tool_name: str
    params: dict


PALABRAS_CLAVE_HORA = ("hora", "fecha", "qué día es", "que dia es")


def interpret(user_text: str) -> ToolCall | None:
    """Traduce texto libre del usuario a una llamada de herramienta.

    Devuelve None si no reconoce ninguna instrucción.
    """
    texto = user_text.lower()

    if any(palabra in texto for palabra in PALABRAS_CLAVE_HORA):
        return ToolCall(tool_name="decir_hora", params={})

    return None
