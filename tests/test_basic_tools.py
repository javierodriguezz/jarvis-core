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


def test_abrir_programa_permitido_llama_popen(monkeypatch):
    llamadas = []
    # monkeypatch reemplaza subprocess.Popen solo durante esta prueba y lo
    # regresa a la normalidad al terminar -- así probamos que se intentó
    # abrir el programa correcto sin abrir de verdad el Bloc de notas.
    monkeypatch.setattr(
        basic_tools.subprocess, "Popen", lambda args: llamadas.append(args)
    )

    resultado = basic_tools.abrir_programa_o_web("Bloc de Notas")

    assert llamadas == [["notepad.exe"]]
    assert "bloc de notas" in resultado.lower()


def test_abrir_sitio_permitido_llama_webbrowser(monkeypatch):
    llamadas = []
    monkeypatch.setattr(
        basic_tools.webbrowser, "open", lambda url: llamadas.append(url)
    )

    resultado = basic_tools.abrir_programa_o_web("youtube")

    assert llamadas == ["https://youtube.com"]
    assert "youtube" in resultado.lower()


def test_abrir_algo_no_permitido_no_ejecuta_nada(monkeypatch):
    def falla_si_se_llama(*_args, **_kwargs):
        raise AssertionError("no debería intentar abrir nada no permitido")

    monkeypatch.setattr(basic_tools.subprocess, "Popen", falla_si_se_llama)
    monkeypatch.setattr(basic_tools.webbrowser, "open", falla_si_se_llama)

    resultado = basic_tools.abrir_programa_o_web("cmd.exe")

    assert "no está en la lista" in resultado
