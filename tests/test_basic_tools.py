"""
Pruebas de las herramientas básicas.

Cada herramienta nueva que agreguemos en jarvis/tools/basic_tools.py debería
tener al menos una prueba aquí antes de darla por "terminada" -- así
practicamos la costumbre de probar cada módulo antes de seguir, como
quedamos en la forma de trabajar del proyecto.
"""

import re
from datetime import datetime

from jarvis.tools import basic_tools


def test_decir_hora_formato():
    resultado = basic_tools.decir_hora()

    assert isinstance(resultado, str)
    assert re.search(r"\d{2}:\d{2}", resultado)


def test_decir_hora_incluye_fecha_de_hoy():
    hoy = datetime.now().strftime("%d/%m/%Y")

    resultado = basic_tools.decir_hora()

    assert hoy in resultado
