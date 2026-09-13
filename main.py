"""
Punto de entrada de Jarvis (v0.1 - consola).

Lee texto de la consola, lo pasa por jarvis.core.interpreter para traducirlo
a una ToolCall, y jarvis.core.executor la valida y ejecuta.

Desde la Fase 3, interpreter.interpret() usa un modelo local vía Ollama, así
que necesita que el servicio de Ollama esté corriendo en la máquina.

Desde la Fase 5, escribir "voz" en vez de una instrucción graba del
micrófono y transcribe con Whisper -- el texto resultante entra al mismo
interpreter.interpret() de siempre, como si se hubiera escrito a mano.

Desde la Fase 6, cada respuesta de Jarvis también se reproduce en voz alta
con Piper, además de imprimirse.

Desde la Fase 6.5, cuando ninguna herramienta local aplica, la pregunta se
manda a una IA en la nube (Gemini) con la herramienta preguntar_ia, en vez de
contestar "no entendí".
"""

import requests
import sounddevice as sd

from jarvis.audio import grabador, sintetizador, transcriptor
from jarvis.core import executor, interpreter
from jarvis.memory import historial_store


def hablar(texto: str) -> None:
    """Imprime una respuesta de Jarvis y la reproduce en voz alta con Piper."""
    print(texto)
    audio, sample_rate = sintetizador.sintetizar(texto)
    sd.play(audio, sample_rate)
    sd.wait()


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
        except requests.ConnectionError:
            respuesta = "No pude conectar con Ollama. ¿Está corriendo el servicio?"
            hablar(respuesta)
            historial_store.agregar_turno(texto, respuesta)
            continue
        except requests.HTTPError as error:
            respuesta = f"Ollama respondió con un error: {error}"
            hablar(respuesta)
            historial_store.agregar_turno(texto, respuesta)
            continue
        except requests.RequestException as error:
            respuesta = f"Error hablando con Ollama: {error}"
            hablar(respuesta)
            historial_store.agregar_turno(texto, respuesta)
            continue

        if tool_call is None:
            # Ninguna herramienta local encajó, o el modelo contestó algo que
            # no se pudo validar. En vez de rendirse con un "no entendí", la
            # pregunta se manda tal cual a la IA en la nube. Sigue pasando por
            # executor.execute() como cualquier otra herramienta: se valida
            # contra el registro y queda en el log, igual que siempre.
            tool_call = interpreter.ToolCall(
                tool_name="preguntar_ia", params={"pregunta": texto}
            )

        respuesta = executor.execute(tool_call)
        hablar(respuesta)
        historial_store.agregar_turno(texto, respuesta)


if __name__ == "__main__":
    main()
