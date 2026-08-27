"""
Punto de entrada de Jarvis (v0.1 - consola).

Por ahora este loop solo repite lo que escribes (echo), para confirmar que
el entorno está bien configurado. En la Fase 1 lo conectamos con
jarvis/core/interpreter.py para que reconozca instrucciones reales.
"""


def main():
    print("Jarvis (v0.1) -- escribe 'salir' para terminar.")
    while True:
        texto = input("> ").strip()
        if texto.lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break
        if not texto:
            continue
        # TODO (Fase 1): reemplazar este echo por una llamada real a
        # jarvis.core.interpreter para interpretar la instrucción.
        print(f"(echo) dijiste: {texto}")


if __name__ == "__main__":
    main()
