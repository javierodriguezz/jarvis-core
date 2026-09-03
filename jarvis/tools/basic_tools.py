"""
Las ~5 herramientas iniciales de la v0.1 (ver docs/ROADMAP.md, Fase 1).

Cada función aquí debe:
  - Tener un docstring claro (el LLM lo usará más adelante para saber cuándo usarla).
  - No confiar en el texto del usuario sin validar (ej. rutas, nombres de programas).
  - No usar os.system / subprocess con shell=True sobre entrada libre del usuario.

Se implementan una por una, empezando por la más simple (hora y fecha).
"""

import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

import config
from jarvis.memory import notes_store

LIMITE_RESULTADOS_BUSQUEDA = 10


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
