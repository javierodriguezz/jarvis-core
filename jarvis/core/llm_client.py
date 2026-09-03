"""
Cliente HTTP para el servicio local de Ollama (Fase 3).

Ollama corre como un programa aparte en segundo plano y expone una API HTTP
en config.OLLAMA_HOST (por defecto http://localhost:11434). Este módulo no
sabe nada de herramientas ni de Jarvis -- solo sabe mandar un texto y
regresar lo que el modelo respondió. La lógica de "qué hacer con esa
respuesta" vive en interpreter.py.
"""

import requests

import config


def generar(prompt: str) -> str:
    """Envía 'prompt' al modelo configurado en Ollama y regresa el texto de respuesta.

    Si el servicio de Ollama no está corriendo, o la petición falla, la
    excepción de requests se deja propagar -- quien llame a esta función
    decide cómo avisarle al usuario (ej. interpreter.py con un mensaje
    claro), no se esconde el error aquí.
    """
    respuesta = requests.post(
        f"{config.OLLAMA_HOST}/api/generate",
        json={
            "model": config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=60,
    )
    respuesta.raise_for_status()
    return respuesta.json()["response"]
