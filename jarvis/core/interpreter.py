"""
Intérprete de instrucciones.

Fase 1: reglas simples (palabras clave / regex) que deciden qué herramienta
llamar y con qué parámetros.

Fase 3: esta misma función se reemplaza internamente por una llamada a un
modelo de lenguaje local (Ollama), pero la firma (lo que recibe y lo que
regresa) se mantiene igual -- por eso el resto del sistema no necesita
cambiar cuando lleguemos a esa fase.
"""

import re
from dataclasses import dataclass


@dataclass
class ToolCall:
    tool_name: str
    params: dict


PALABRAS_CLAVE_HORA = ("hora", "fecha", "qué día es", "que dia es")
PALABRAS_CLAVE_ABRIR = ("abre ", "abrir ")
PALABRAS_CLAVE_CONSULTAR_NOTAS = (
    "mis notas",
    "las notas",
    "qué notas tengo",
    "que notas tengo",
)
PALABRAS_CLAVE_BUSCAR_ARCHIVO = (
    "busca archivo ",
    "buscar archivo ",
    "encuentra archivo ",
)
PALABRAS_CLAVE_BORRAR_NOTA = (
    "borra la nota ",
    "borra nota ",
    "elimina la nota ",
    "elimina nota ",
)
PREFIJOS_SOBRESCRIBIR_NOTA = (
    "sobrescribe la nota ",
    "sobrescribe nota ",
    "cambia la nota ",
    "actualiza la nota ",
)
# Después del prefijo espera "<número> con <texto nuevo>", ej. "2 con comprar leche".
PATRON_SOBRESCRIBIR_NOTA = re.compile(r"^(\d+)\s+con\s+(.+)$", re.IGNORECASE)
PALABRAS_CLAVE_PREGUNTA = (
    "cómo te llamas",
    "como te llamas",
    "quién te hizo",
    "quien te hizo",
    "qué puedes hacer",
    "que puedes hacer",
    "cuánto es",
    "cuanto es",
    "cuánto son",
    "cuanto son",
)
# Prefijos más específicos primero, para no dejar un "que" colgando en el
# texto de la nota (ej. "anota que hoy es viernes" -> "hoy es viernes").
PREFIJOS_CREAR_NOTA = ("anota que ", "apunta que ", "anota ", "apunta ")


def interpret(user_text: str) -> ToolCall | None:
    """Traduce texto libre del usuario a una llamada de herramienta.

    Devuelve None si no reconoce ninguna instrucción.
    """
    texto = user_text.lower()

    if any(palabra in texto for palabra in PALABRAS_CLAVE_HORA):
        return ToolCall(tool_name="decir_hora", params={})

    for palabra in PALABRAS_CLAVE_ABRIR:
        if palabra in texto:
            # Todo lo que sigue a "abre"/"abrir" es el nombre a buscar en la
            # lista blanca; el intérprete no valida esa lista, solo extrae
            # la intención -- validar es trabajo de la herramienta.
            nombre = texto.split(palabra, 1)[1].strip()
            return ToolCall(tool_name="abrir_programa_o_web", params={"nombre": nombre})

    if any(palabra in texto for palabra in PALABRAS_CLAVE_CONSULTAR_NOTAS):
        return ToolCall(tool_name="consultar_notas", params={})

    for palabra in PALABRAS_CLAVE_BORRAR_NOTA:
        if palabra in texto:
            numero = texto.split(palabra, 1)[1].strip()
            return ToolCall(tool_name="borrar_nota", params={"numero": numero})

    for prefijo in PREFIJOS_SOBRESCRIBIR_NOTA:
        if prefijo in texto:
            # user_text para conservar mayúsculas/acentos del texto nuevo;
            # la posición del prefijo es la misma en texto y user_text
            # porque .lower() no cambia la longitud de estos caracteres.
            inicio = texto.find(prefijo) + len(prefijo)
            resto = user_text[inicio:].strip()
            coincidencia = PATRON_SOBRESCRIBIR_NOTA.match(resto)
            if coincidencia:
                numero, texto_nuevo = coincidencia.groups()
                return ToolCall(
                    tool_name="sobrescribir_nota",
                    params={"numero": numero, "texto_nuevo": texto_nuevo},
                )

    for palabra in PALABRAS_CLAVE_BUSCAR_ARCHIVO:
        if palabra in texto:
            nombre = texto.split(palabra, 1)[1].strip()
            return ToolCall(tool_name="buscar_archivos", params={"nombre": nombre})

    if any(palabra in texto for palabra in PALABRAS_CLAVE_PREGUNTA):
        return ToolCall(tool_name="responder_pregunta", params={"pregunta": user_text})

    for prefijo in PREFIJOS_CREAR_NOTA:
        if texto.startswith(prefijo):
            # user_text (no texto) para conservar mayúsculas/acentos originales
            # de la nota -- texto solo sirve para hacer el match en minúsculas.
            texto_nota = user_text[len(prefijo):].strip()
            return ToolCall(tool_name="crear_nota", params={"texto": texto_nota})

    return None
