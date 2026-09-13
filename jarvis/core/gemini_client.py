"""
Cliente HTTP para la API de Gemini (Fase 6.5).

Mismo principio que llm_client.py (el cliente de Ollama): este módulo no sabe
nada de herramientas ni de Jarvis -- solo manda una pregunta y regresa lo que
respondió el modelo. Si la petición falla, la excepción se deja propagar;
quien llame decide cómo avisarle al usuario (jarvis/tools/ia_tools.py).

Diferencia importante con Ollama: esto sale a internet. La pregunta viaja a
un servidor de Google, no se queda en esta máquina.
"""

import requests

import config

# El modelo va dentro de la propia URL, y la acción (generateContent) va
# pegada al nombre del modelo con ":". Ejemplo de URL completa:
# https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def generar(pregunta: str, instruccion_sistema: str | None = None) -> str:
    """Envía 'pregunta' al modelo de Gemini configurado y regresa su respuesta en texto.

    'instruccion_sistema' es opcional y sirve para decirle al modelo cómo debe
    comportarse en general (tono, formato, idioma), aparte de la pregunta
    concreta. Igual que en llm_client.py, este módulo no decide qué decirle al
    modelo: solo lo manda. Quien arma esas instrucciones es
    jarvis/tools/ia_tools.py.

    La clave de API viaja en un header (x-goog-api-key) y no pegada a la URL:
    las URLs terminan escritas en los logs de cualquier servidor intermedio,
    los headers no.

    Si no hay internet, si la clave es inválida o si el modelo no existe, la
    excepción de requests se deja propagar (igual que en llm_client.py). Si
    Gemini contesta pero sin texto utilizable, se levanta ValueError.
    """
    cuerpo = {"contents": [{"parts": [{"text": pregunta}]}]}
    if instruccion_sistema:
        cuerpo["systemInstruction"] = {"parts": [{"text": instruccion_sistema}]}

    respuesta = requests.post(
        f"{API_BASE}/{config.GEMINI_MODEL}:generateContent",
        headers={"x-goog-api-key": config.GEMINI_API_KEY},
        json=cuerpo,
        timeout=30,
    )
    respuesta.raise_for_status()
    return _extraer_texto(respuesta.json())


def _extraer_texto(datos: dict) -> str:
    """Saca el texto de la respuesta de Gemini, que viene anidada en varios niveles.

    La forma normal es:
        {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}

    Pero Gemini puede contestar 200 y aun así no traer texto (por ejemplo si
    sus filtros de seguridad bloquearon la pregunta), así que no se da por
    hecho que las llaves existan: si no hay texto, se dice explícitamente en
    vez de reventar con un KeyError a media conversación.
    """
    candidatos = datos.get("candidates", [])
    if not candidatos:
        raise ValueError("Gemini no devolvió ninguna respuesta.")

    partes = candidatos[0].get("content", {}).get("parts", [])
    textos = [parte["text"] for parte in partes if "text" in parte]
    if not textos:
        raise ValueError("Gemini devolvió una respuesta sin texto.")

    return "".join(textos).strip()
