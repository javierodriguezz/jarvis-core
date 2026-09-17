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

Desde la Fase 7, escribir "escuchar" entra al modo manos libres: Jarvis se
queda esperando la palabra de activación ("hey Jarvis") y solo entonces graba.
Ctrl+C regresa al prompt de texto, que se conserva porque sigue siendo la
forma más cómoda de probar y depurar.
"""

import requests
import sounddevice as sd

from jarvis.audio import detector, grabador, sintetizador, transcriptor
from jarvis.core import executor, interpreter
from jarvis.memory import historial_store


def hablar(texto: str) -> None:
    """Imprime una respuesta de Jarvis y la reproduce en voz alta con Piper."""
    print(texto)
    audio, sample_rate = sintetizador.sintetizar(texto)
    sd.play(audio, sample_rate)
    sd.wait()


def _responder(entrada: str, respuesta: str) -> None:
    """Dice la respuesta en voz alta y guarda el turno en el historial."""
    hablar(respuesta)
    historial_store.agregar_turno(entrada, respuesta)


def procesar_texto(texto: str) -> None:
    """
    Pasa una instrucción ya en texto por la tubería completa de Jarvis:
    interpretar -> ejecutar -> responder en voz alta -> guardar en el historial.

    No le importa de dónde salió el texto (teclado, comando "voz" o palabra de
    activación), por eso los tres modos la reutilizan en vez de duplicar esto.
    """
    # Sin esto la consola se queda muda varios segundos (Ollama tarda ~2s, y
    # bastante más si tiene que cargar el modelo a memoria) y parece colgada.
    print("Pensando...", flush=True)
    try:
        tool_call = interpreter.interpret(texto)
    except requests.ConnectionError:
        _responder(texto, "No pude conectar con Ollama. ¿Está corriendo el servicio?")
        return
    except requests.HTTPError as error:
        _responder(texto, f"Ollama respondió con un error: {error}")
        return
    except requests.RequestException as error:
        _responder(texto, f"Error hablando con Ollama: {error}")
        return

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
    print("Respondiendo...", flush=True)
    _responder(texto, respuesta)


def escuchar_una_vez(cuenta_regresiva: bool) -> str:
    """
    Graba del micrófono y regresa lo transcrito (cadena vacía si no se oyó nada).

    cuenta_regresiva se apaga en el modo manos libres: ahí el usuario acaba de
    decir la palabra de activación y ya viene hablando.
    """
    audio = grabador.grabar_audio(cuenta_regresiva=cuenta_regresiva)
    print("Transcribiendo...", flush=True)
    return transcriptor.transcribir(audio)


def modo_escucha() -> None:
    """
    Modo manos libres (Fase 7): espera "hey Jarvis" y solo entonces graba.

    El detector es un modelo diminuto que corre continuo sin cargar el CPU;
    Whisper, que sí es pesado, solo se despierta después de la activación.
    Se sale con Ctrl+C, que regresa al prompt de texto.
    """
    print("Modo escucha: di 'hey Jarvis' para activarme. Ctrl+C para volver al teclado.")
    try:
        while True:
            detector.esperar_palabra_activacion()
            # "¿Sí?" hace de campanita: le avisa al usuario que ya está grabando.
            hablar("¿Sí?")
            texto = escuchar_una_vez(cuenta_regresiva=False)
            if not texto:
                hablar("No escuché nada.")
                continue
            print(f"Escuché: {texto}")
            procesar_texto(texto)
    except KeyboardInterrupt:
        print("\nSalí del modo escucha.")


def main():
    print(
        "Jarvis (v0.1) -- 'salir' para terminar, 'voz' para hablar una vez, "
        "'escuchar' para modo manos libres."
    )
    while True:
        texto = input("> ").strip()
        if texto.lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break

        if texto.lower() == "escuchar":
            modo_escucha()
            continue

        if texto.lower() == "voz":
            texto = escuchar_una_vez(cuenta_regresiva=True)
            if not texto:
                print("No escuché nada.")
                continue
            print(f"Escuché: {texto}")

        if not texto:
            continue

        procesar_texto(texto)


if __name__ == "__main__":
    main()
