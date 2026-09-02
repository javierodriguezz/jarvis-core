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

import config


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


# TODO (Fase 1, paso 3): crear_nota(texto) / consultar_notas()
