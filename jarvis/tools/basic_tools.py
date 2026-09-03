"""
Las ~5 herramientas iniciales de la v0.1 (ver docs/ROADMAP.md, Fase 1).

Cada función aquí debe:
  - Tener un docstring claro (el LLM lo usará más adelante para saber cuándo usarla).
  - No confiar en el texto del usuario sin validar (ej. rutas, nombres de programas).
  - No usar os.system / subprocess con shell=True sobre entrada libre del usuario.

Se implementan una por una, empezando por la más simple (hora y fecha).
"""

import ast
import operator
import re
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

import config
from jarvis.memory import notes_store

LIMITE_RESULTADOS_BUSQUEDA = 10

# Preguntas fijas que Jarvis sabe responder sin cálculo. Duplicamos las
# variantes con y sin acento (igual que en interpreter.py) porque todavía no
# normalizamos acentos en ningún lado del proyecto.
RESPUESTAS_PREDEFINIDAS = {
    "cómo te llamas": "Me llamo Jarvis.",
    "como te llamas": "Me llamo Jarvis.",
    "quién te hizo": "Me construyó Javier, programando en Python.",
    "quien te hizo": "Me construyó Javier, programando en Python.",
    "qué puedes hacer": (
        "Puedo decirte la hora, abrir programas o páginas web, guardar y "
        "consultar notas, buscar archivos, y hacer cálculos simples."
    ),
    "que puedes hacer": (
        "Puedo decirte la hora, abrir programas o páginas web, guardar y "
        "consultar notas, buscar archivos, y hacer cálculos simples."
    ),
}

# Únicos operadores que _evaluar_nodo tiene permitido ejecutar. Cualquier
# nodo del árbol de sintaxis que no esté en este mapa (nombres de variable,
# llamadas a función, imports, etc.) hace que se rechace la expresión.
_OPERADORES_PERMITIDOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def decir_hora() -> str:
    """Devuelve la fecha y hora actuales del sistema en formato legible."""
    ahora = datetime.now()
    return ahora.strftime("Son las %H:%M del %d/%m/%Y")


def abrir_programa_o_web(nombre: str) -> str:
    """Abre un programa o una página web, solo si 'nombre' está en la lista blanca.

    Nunca ejecuta texto libre del usuario: 'nombre' se busca en
    config.PROGRAMAS_PERMITIDOS y config.SITIOS_PERMITIDOS, y solo si hay
    coincidencia exacta se abre el ejecutable o la URL correspondiente.
    """
    clave = nombre.strip().lower()

    if clave in config.PROGRAMAS_PERMITIDOS:
        ejecutable = config.PROGRAMAS_PERMITIDOS[clave]
        subprocess.Popen([ejecutable])
        return f"Abriendo {clave}."

    if clave in config.SITIOS_PERMITIDOS:
        url = config.SITIOS_PERMITIDOS[clave]
        webbrowser.open(url)
        return f"Abriendo {clave}."

    return f"'{nombre}' no está en la lista de programas o sitios permitidos."


def crear_nota(texto: str) -> str:
    """Guarda una nota nueva en el almacenamiento de notas (data/notes.json)."""
    texto = texto.strip()
    if not texto:
        return "No puedo guardar una nota vacía."

    notes_store.add_note(texto)
    return f"Nota guardada: {texto}"


def consultar_notas() -> str:
    """Devuelve todas las notas guardadas como una lista numerada legible."""
    notas = notes_store.list_notes()
    if not notas:
        return "No tienes notas guardadas."

    lineas = [f"{i}. {nota['texto']}" for i, nota in enumerate(notas, start=1)]
    return "\n".join(lineas)


def borrar_nota(numero: str) -> str:
    """Borra la nota con el número indicado (el mismo que muestra consultar_notas).

    Es una acción destructiva -- se registra con permiso CONFIRM en
    registry.py, así que executor.py pide confirmación antes de llamarla.
    """
    numero = numero.strip()
    if not numero.isdigit():
        return f"'{numero}' no es un número de nota válido."

    nota = notes_store.delete_note(int(numero))
    if nota is None:
        return f"No encontré ninguna nota con el número {numero}."

    return f"Nota {numero} borrada: {nota['texto']}"


def sobrescribir_nota(numero: str, texto_nuevo: str) -> str:
    """Reemplaza el texto de la nota con el número indicado por texto_nuevo.

    Es una acción destructiva (se pierde el texto anterior de la nota) --
    se registra con permiso CONFIRM en registry.py, así que executor.py
    pide confirmación antes de llamarla.
    """
    numero = numero.strip()
    if not numero.isdigit():
        return f"'{numero}' no es un número de nota válido."

    texto_nuevo = texto_nuevo.strip()
    if not texto_nuevo:
        return "No puedo dejar una nota vacía; dime el texto nuevo."

    nota = notes_store.update_note(int(numero), texto_nuevo)
    if nota is None:
        return f"No encontré ninguna nota con el número {numero}."

    return f"Nota {numero} actualizada: {nota['texto']}"


def buscar_archivos(nombre: str) -> str:
    """Busca archivos cuyo nombre contenga 'nombre' dentro de las carpetas permitidas.

    Solo revisa las carpetas listadas en config.ALLOWED_SEARCH_DIRS (nunca el
    disco completo). Si alguna de esas carpetas no existe en esta máquina, se
    avisa en el resultado pero se sigue buscando en las demás. Se detiene al
    llegar a LIMITE_RESULTADOS_BUSQUEDA coincidencias para no inundar la
    respuesta si el nombre es muy genérico.
    """
    nombre = nombre.strip().lower()
    if not nombre:
        return "Dime qué archivo buscar."

    encontrados = []
    carpetas_faltantes = []

    for carpeta in config.ALLOWED_SEARCH_DIRS:
        ruta_carpeta = Path(carpeta)
        if not ruta_carpeta.exists():
            carpetas_faltantes.append(carpeta)
            continue

        for ruta in ruta_carpeta.rglob("*"):
            if ruta.is_file() and nombre in ruta.name.lower():
                encontrados.append(str(ruta))
                if len(encontrados) >= LIMITE_RESULTADOS_BUSQUEDA:
                    break
        if len(encontrados) >= LIMITE_RESULTADOS_BUSQUEDA:
            break

    lineas = []
    if encontrados:
        lineas.append(f"Encontré {len(encontrados)} archivo(s):")
        lineas.extend(f"- {ruta}" for ruta in encontrados)
    else:
        lineas.append(f"No encontré archivos con '{nombre}'.")

    if carpetas_faltantes:
        lineas.append(f"No pude revisar (no existen): {', '.join(carpetas_faltantes)}")

    return "\n".join(lineas)


def _evaluar_nodo(nodo):
    """Evalúa recursivamente un nodo del árbol de sintaxis de una expresión aritmética.

    Solo entiende números y los operadores de _OPERADORES_PERMITIDOS. Cualquier
    otro tipo de nodo (nombres de variable, llamadas a función, comparaciones,
    etc.) levanta ValueError -- así nunca se ejecuta nada que no sea aritmética
    pura, a diferencia de lo que pasaría con eval() sobre texto libre.
    """
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)):
        return nodo.value
    if isinstance(nodo, ast.BinOp) and type(nodo.op) in _OPERADORES_PERMITIDOS:
        return _OPERADORES_PERMITIDOS[type(nodo.op)](
            _evaluar_nodo(nodo.left), _evaluar_nodo(nodo.right)
        )
    if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in _OPERADORES_PERMITIDOS:
        return _OPERADORES_PERMITIDOS[type(nodo.op)](_evaluar_nodo(nodo.operand))
    raise ValueError("Expresión no permitida")


def _evaluar_expresion_matematica(expresion: str) -> float:
    """Evalúa una expresión aritmética simple (+ - * /) de forma segura.

    Se parsea el texto a un árbol de sintaxis con ast.parse (mode="eval") y
    se recorre con _evaluar_nodo, que solo permite números y operadores
    aritméticos básicos. Levanta ValueError o SyntaxError si la expresión
    trae algo fuera de eso.
    """
    # ast.parse en modo "eval" no tolera espacios iniciales (los interpreta
    # como indentación inesperada), así que se recortan antes de parsear.
    arbol = ast.parse(expresion.strip(), mode="eval")
    return _evaluar_nodo(arbol.body)


def responder_pregunta(pregunta: str) -> str:
    """Responde una pregunta sencilla: predefinida o un cálculo aritmético simple.

    Primero busca coincidencia en RESPUESTAS_PREDEFINIDAS. Si no hay, se
    queda solo con los dígitos y operadores del texto e intenta evaluarlo
    como expresión aritmética con _evaluar_expresion_matematica. Si nada de
    eso aplica, admite que no sabe responder.
    """
    texto = pregunta.strip().lower()

    for clave, respuesta in RESPUESTAS_PREDEFINIDAS.items():
        if clave in texto:
            return respuesta

    expresion = re.sub(r"[^0-9+\-*/.() ]", "", texto)
    if expresion.strip():
        try:
            resultado = _evaluar_expresion_matematica(expresion)
            if isinstance(resultado, float) and resultado.is_integer():
                resultado = int(resultado)
            return f"El resultado es {resultado}."
        except (ValueError, SyntaxError, ZeroDivisionError, TypeError):
            pass

    return "No sé responder eso todavía."
