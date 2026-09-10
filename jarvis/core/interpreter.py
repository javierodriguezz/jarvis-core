"""
Intérprete de instrucciones.

Fase 1-2: reglas simples (palabras clave / regex).

Fase 3 (actual): interpret() usa un modelo de lenguaje local vía Ollama
(jarvis/core/llm_client.py) para decidir qué herramienta llamar y con qué
parámetros. La firma de interpret() (lo que recibe y lo que regresa) es la
misma de siempre -- por eso executor.py y main.py no cambiaron nada.

Regla importante: nunca se confía ciegamente en lo que responde el modelo.
Todo lo que dice se valida contra jarvis/tools/registry.py (la lista blanca
real) antes de convertirse en un ToolCall. Si algo no cuadra -- JSON mal
formado, herramienta inventada, parámetros que no corresponden -- se trata
igual que "no entendí" (se regresa None), nunca se ejecuta a ciegas.
"""

import inspect
import json
from dataclasses import dataclass

from jarvis.core import llm_client
from jarvis.tools import registry


@dataclass
class ToolCall:
    tool_name: str
    params: dict


PROMPT_BASE = """Eres el intérprete de un asistente llamado Jarvis. Tu única tarea es decidir qué herramienta de la siguiente lista corresponde a la instrucción del usuario, y con qué parámetros.

Herramientas disponibles:
{herramientas}

Reglas:
- Responde ÚNICAMENTE con un objeto JSON, sin texto antes ni después, sin explicaciones.
- El formato exacto es: {{"tool_name": "<nombre_de_la_herramienta>", "params": {{...}}}}
- Los parámetros deben ser exactamente los que pide la herramienta elegida, como texto (string).
- Si ninguna herramienta aplica a la instrucción, responde exactamente: {{"tool_name": null, "params": {{}}}}

Ejemplos:
Instrucción: "qué hora es"
Respuesta: {{"tool_name": "decir_hora", "params": {{}}}}

Instrucción: "abre youtube"
Respuesta: {{"tool_name": "abrir_programa_o_web", "params": {{"nombre": "youtube"}}}}

Instrucción: "abre la calculadora"
Respuesta: {{"tool_name": "abrir_programa_o_web", "params": {{"nombre": "calculadora"}}}}

Instrucción: "anota que hoy es viernes"
Respuesta: {{"tool_name": "crear_nota", "params": {{"texto": "hoy es viernes"}}}}

Instrucción: "cuéntame un chiste"
Respuesta: {{"tool_name": null, "params": {{}}}}

Instrucción del usuario: "{instruccion}"
Respuesta:"""


def _describir_herramientas() -> str:
    """Arma la lista de herramientas y sus parámetros para meterla en el prompt.

    Los parámetros se sacan con inspect.signature() directo de la función
    real registrada, no se escriben a mano -- así el prompt nunca se
    desincroniza de lo que basic_tools.py realmente espera.
    """
    lineas = []
    for nombre, entrada in registry.TOOLS.items():
        parametros = list(inspect.signature(entrada["func"]).parameters.keys())
        parametros_texto = ", ".join(parametros) if parametros else "ninguno"
        lineas.append(f"- {nombre}: {entrada['description']} (parámetros: {parametros_texto})")
    return "\n".join(lineas)


def _extraer_bloque_json(texto: str) -> str | None:
    """Recorta desde la primera '{' hasta la última '}' de 'texto'.

    Los modelos chicos a veces agregan texto extra alrededor del JSON aunque
    se les pida que no lo hagan; esto rescata el bloque aunque venga rodeado
    de prosa. Si no hay ni un '{' o un '}', regresa None.
    """
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio == -1 or fin == -1 or fin < inicio:
        return None
    return texto[inicio : fin + 1]


def _parsear_respuesta_llm(texto_llm: str) -> ToolCall | None:
    """Convierte la respuesta cruda del modelo en un ToolCall, o None si no se puede confiar en ella.

    Aquí es donde se aplica la regla de "nunca confiar ciegamente en la
    salida de un modelo": se verifica que sea JSON válido, que tool_name
    exista de verdad en registry.TOOLS, y que params traiga exactamente los
    nombres que esa herramienta espera -- ni más ni menos.
    """
    bloque = _extraer_bloque_json(texto_llm)
    if bloque is None:
        return None

    try:
        datos = json.loads(bloque)
    except json.JSONDecodeError:
        return None

    if not isinstance(datos, dict):
        return None

    tool_name = datos.get("tool_name")
    params = datos.get("params", {})

    if not isinstance(tool_name, str) or tool_name not in registry.TOOLS:
        return None
    if not isinstance(params, dict):
        return None

    parametros_esperados = set(inspect.signature(registry.TOOLS[tool_name]["func"]).parameters)
    if set(params.keys()) != parametros_esperados:
        return None
    if not all(isinstance(valor, str) for valor in params.values()):
        return None

    return ToolCall(tool_name=tool_name, params=params)


def interpret(user_text: str) -> ToolCall | None:
    """Traduce texto libre del usuario a una llamada de herramienta, usando el LLM local.

    Si Ollama no está corriendo o la petición falla, la excepción de
    requests se deja propagar (llm_client.generar no la esconde) -- quien
    llame a interpret() (main.py) decide cómo avisarle al usuario que el
    problema es de conexión, distinto de "no entendí la instrucción".
    """
    prompt = PROMPT_BASE.format(
        herramientas=_describir_herramientas(), instruccion=user_text
    )
    respuesta = llm_client.generar(prompt)
    return _parsear_respuesta_llm(respuesta)
