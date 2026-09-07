"""
Punto de entrada de Jarvis (v0.1 - consola).

Lee texto de la consola, lo pasa por jarvis.core.interpreter para traducirlo
a una ToolCall, y jarvis.core.executor la valida y ejecuta.

Desde la Fase 3, interpreter.interpret() usa un modelo local vía Ollama, así
que necesita que el servicio de Ollama esté corriendo en la máquina.
"""

import requests

from jarvis.core import executor, interpreter
from jarvis.memory import historial_store


def main():
    print("Jarvis (v0.1) -- escribe 'salir' para terminar.")
    while True:
        texto = input("> ").strip()
        if texto.lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break
        if not texto:
            continue

        try:
            tool_call = interpreter.interpret(texto)
        except requests.RequestException:
            respuesta = "No pude conectar con Ollama. ¿Está corriendo el servicio?"
            print(respuesta)
            historial_store.agregar_turno(texto, respuesta)
            continue

        if tool_call is None:
            respuesta = "No entendí esa instrucción."
            print(respuesta)
            historial_store.agregar_turno(texto, respuesta)
            continue

        respuesta = executor.execute(tool_call)
        print(respuesta)
        historial_store.agregar_turno(texto, respuesta)


if __name__ == "__main__":
    main()
