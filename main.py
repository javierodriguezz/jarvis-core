"""
Punto de entrada de Jarvis (v0.1 - consola).

Lee texto de la consola, lo pasa por jarvis.core.interpreter para traducirlo
a una ToolCall, y jarvis.core.executor la valida y ejecuta.

Desde la Fase 3, interpreter.interpret() usa un modelo local vía Ollama, así
que necesita que el servicio de Ollama esté corriendo en la máquina.

Desde la Fase 5, escribir "voz" en vez de una instrucción graba del
micrófono y transcribe con Whisper -- el texto resultante entra al mismo
interpreter.interpret() de siempre, como si se hubiera escrito a mano.
"""

import requests

from jarvis.audio import grabador, transcriptor
from jarvis.core import executor, interpreter
from jarvis.memory import historial_store


def main():
    print("Jarvis (v0.1) -- escribe 'salir' para terminar, 'voz' para hablar.")
    while True:
        texto = input("> ").strip()
        if texto.lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break

        if texto.lower() == "voz":
            audio = grabador.grabar_audio()
            texto = transcriptor.transcribir(audio)
            if not texto:
                print("No escuché nada.")
                continue
            print(f"Escuché: {texto}")

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
