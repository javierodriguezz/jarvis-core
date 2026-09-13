"""
Herramienta que conecta a Jarvis con una IA en la nube (Fase 6.5).

A diferencia de basic_tools.py, esta herramienta no resuelve nada localmente:
manda la pregunta a la API de Gemini (jarvis/core/gemini_client.py) y regresa
lo que conteste.

Dos reglas que se cumplen aquí:

1. Nunca lanza una excepción, siempre regresa un string. executor.execute()
   llama a la función sin try/except alrededor, así que una excepción que se
   escape tumbaría el loop de main.py a media conversación.
2. Los mensajes de error están escritos para escucharse, no solo para leerse
   (Fase 6): nada de URLs ni de texto crudo de excepciones, que en voz alta
   se convierten en una ristra de letras y diagonales.
"""

import re

import requests

import config
from jarvis.core import gemini_client

# Gemini, si no se le dice nada, responde en Markdown y se extiende bastante:
# encabezados, listas con viñetas, palabras en negritas. Todo eso, leído en voz
# alta por Piper, se convierte en asteriscos dictados y respuestas eternas.
INSTRUCCION_DE_VOZ = (
    "Eres Jarvis, un asistente personal. Tu respuesta se va a leer en voz alta, "
    "así que responde siempre en español, en texto plano corrido, sin Markdown, "
    "sin asteriscos, sin encabezados, sin listas con viñetas y sin emojis. "
    "Sé breve: dos o tres frases, salvo que te pidan explícitamente más detalle."
)


def preguntar_ia(pregunta: str) -> str:
    """Responde preguntas generales o de conocimiento usando una IA en la nube (Gemini).

    Úsala para dudas abiertas que ninguna otra herramienta cubre: qué es algo,
    por qué pasa algo, explicaciones, recomendaciones. No es para la hora, las
    notas, abrir programas ni cálculos simples -- eso ya lo resuelven las
    otras herramientas sin salir a internet.

    Es la única herramienta que manda texto del usuario fuera de esta máquina.
    """
    if not config.GEMINI_API_KEY:
        return (
            "No tengo configurada la clave de Gemini. "
            "Hay que ponerla en el archivo de configuración del proyecto."
        )

    try:
        return _quitar_markdown(gemini_client.generar(pregunta, INSTRUCCION_DE_VOZ))
    except requests.ConnectionError:
        return "No pude conectar con Gemini. Revisa tu conexión a internet."
    except requests.Timeout:
        return "Gemini tardó demasiado en responder."
    except requests.HTTPError as error:
        return _mensaje_de_error_http(error)
    except requests.RequestException:
        return "Hubo un problema al hablar con Gemini."
    except ValueError as error:
        # Los ValueError vienen de gemini_client._extraer_texto y ya traen un
        # mensaje corto y legible en voz alta.
        return str(error)


def _quitar_markdown(texto: str) -> str:
    """Quita las marcas de Markdown que el modelo mete aunque se le pida texto plano.

    Es el cinturón además de los tirantes: la instrucción de arriba ya le pide
    texto plano, pero un modelo puede ignorarla, y un solo par de asteriscos
    arruina la respuesta hablada. Solo se quitan asteriscos, acentos graves y
    almohadillas de encabezado; los guiones bajos se dejan en paz porque
    aparecen en nombres reales (archivo_de_prueba) y quitarlos haría más daño
    que bien.
    """
    sin_codigo = texto.replace("`", "")
    sin_enfasis = re.sub(r"\*+", "", sin_codigo)
    sin_encabezados = re.sub(r"^#{1,6}\s*", "", sin_enfasis, flags=re.MULTILINE)
    return sin_encabezados.strip()


# Cada código HTTP apunta a una causa distinta, y el mensaje tiene que mandar
# a buscar al lugar correcto. Un 503 no se arregla revisando la clave.
_MENSAJES_POR_CODIGO = {
    400: "Gemini no entendió la petición. Es un problema del programa, no de lo que preguntaste.",
    403: "Gemini rechazó la clave de API. Hay que revisar que siga siendo válida.",
    404: "Gemini no encontró el modelo configurado. Hay que revisar el nombre del modelo.",
    429: "Se agotó la cuota gratuita de Gemini por ahora. Hay que esperar un rato.",
    503: "Gemini está saturado en este momento. Vuelve a intentar en un minuto.",
}


def _mensaje_de_error_http(error: requests.HTTPError) -> str:
    """Traduce un error HTTP de Gemini a algo que se entienda al escucharlo.

    Dos razones para no usar el texto que trae la excepción tal cual:

    1. Incluye la URL completa de la petición, y Jarvis lee sus respuestas en
       voz alta -- una URL dictada letra por letra no le sirve a nadie.
    2. El código dice dónde está el problema, y mandar a revisar el lugar
       equivocado hace perder tiempo: 403 es la clave, 404 el modelo, 429 la
       cuota agotada, y 503 que los servidores de Google están saturados
       (ahí no hay nada que arreglar, solo esperar).
    """
    if error.response is None:
        return "Gemini respondió con un error que no supe interpretar."

    codigo = error.response.status_code
    return _MENSAJES_POR_CODIGO.get(codigo, f"Gemini respondió con un error {codigo}.")
