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


def test_crear_nota_guarda_y_confirma(tmp_path, monkeypatch):
    monkeypatch.setattr(basic_tools.notes_store.db, "DB_FILE", tmp_path / "jarvis.db")

    resultado = basic_tools.crear_nota("comprar pan")

    assert "comprar pan" in resultado
    assert basic_tools.notes_store.list_notes()[0]["texto"] == "comprar pan"


def test_crear_nota_vacia_no_guarda_nada(tmp_path, monkeypatch):
    monkeypatch.setattr(basic_tools.notes_store.db, "DB_FILE", tmp_path / "jarvis.db")

    resultado = basic_tools.crear_nota("   ")

    assert basic_tools.notes_store.list_notes() == []
    assert "vacía" in resultado


def test_consultar_notas_sin_notas(tmp_path, monkeypatch):
    monkeypatch.setattr(basic_tools.notes_store.db, "DB_FILE", tmp_path / "jarvis.db")

    resultado = basic_tools.consultar_notas()

    assert "no tienes notas" in resultado.lower()


def test_consultar_notas_con_notas(tmp_path, monkeypatch):
    monkeypatch.setattr(basic_tools.notes_store.db, "DB_FILE", tmp_path / "jarvis.db")
    basic_tools.crear_nota("primera")
    basic_tools.crear_nota("segunda")

    resultado = basic_tools.consultar_notas()

    assert "primera" in resultado
    assert "segunda" in resultado


def test_borrar_nota_valida(tmp_path, monkeypatch):
    monkeypatch.setattr(basic_tools.notes_store.db, "DB_FILE", tmp_path / "jarvis.db")
    basic_tools.crear_nota("comprar pan")

    resultado = basic_tools.borrar_nota("1")

    assert "comprar pan" in resultado
    assert basic_tools.notes_store.list_notes() == []


def test_borrar_nota_numero_inexistente(tmp_path, monkeypatch):
    monkeypatch.setattr(basic_tools.notes_store.db, "DB_FILE", tmp_path / "jarvis.db")

    resultado = basic_tools.borrar_nota("5")

    assert "no encontré" in resultado.lower()


def test_borrar_nota_numero_invalido_no_llama_notes_store(monkeypatch):
    def falla_si_se_llama(*_args, **_kwargs):
        raise AssertionError("no debería tocar notes_store con un número inválido")

    monkeypatch.setattr(basic_tools.notes_store, "delete_note", falla_si_se_llama)

    resultado = basic_tools.borrar_nota("dos")

    assert "no es un número" in resultado.lower()


def test_sobrescribir_nota_valida(tmp_path, monkeypatch):
    monkeypatch.setattr(basic_tools.notes_store.db, "DB_FILE", tmp_path / "jarvis.db")
    basic_tools.crear_nota("comprar pan")

    resultado = basic_tools.sobrescribir_nota("1", "comprar leche")

    assert "comprar leche" in resultado
    assert basic_tools.notes_store.list_notes()[0]["texto"] == "comprar leche"


def test_sobrescribir_nota_numero_inexistente(tmp_path, monkeypatch):
    monkeypatch.setattr(basic_tools.notes_store.db, "DB_FILE", tmp_path / "jarvis.db")

    resultado = basic_tools.sobrescribir_nota("5", "texto nuevo")

    assert "no encontré" in resultado.lower()


def test_sobrescribir_nota_numero_invalido_no_llama_notes_store(monkeypatch):
    def falla_si_se_llama(*_args, **_kwargs):
        raise AssertionError("no debería tocar notes_store con un número inválido")

    monkeypatch.setattr(basic_tools.notes_store, "update_note", falla_si_se_llama)

    resultado = basic_tools.sobrescribir_nota("dos", "texto nuevo")

    assert "no es un número" in resultado.lower()


def test_sobrescribir_nota_texto_vacio_no_llama_notes_store(monkeypatch):
    def falla_si_se_llama(*_args, **_kwargs):
        raise AssertionError("no debería tocar notes_store con texto vacío")

    monkeypatch.setattr(basic_tools.notes_store, "update_note", falla_si_se_llama)

    resultado = basic_tools.sobrescribir_nota("1", "   ")

    assert "vacía" in resultado.lower()


def test_buscar_archivos_encuentra_coincidencia(tmp_path, monkeypatch):
    carpeta = tmp_path / "Desktop"
    carpeta.mkdir()
    (carpeta / "reporte_final.txt").write_text("contenido")
    (carpeta / "otro.txt").write_text("contenido")
    monkeypatch.setattr(basic_tools.config, "ALLOWED_SEARCH_DIRS", [str(carpeta)])

    resultado = basic_tools.buscar_archivos("reporte")

    assert "reporte_final.txt" in resultado
    assert "otro.txt" not in resultado


def test_buscar_archivos_sin_coincidencias(tmp_path, monkeypatch):
    carpeta = tmp_path / "Desktop"
    carpeta.mkdir()
    monkeypatch.setattr(basic_tools.config, "ALLOWED_SEARCH_DIRS", [str(carpeta)])

    resultado = basic_tools.buscar_archivos("inexistente")

    assert "no encontré" in resultado.lower()


def test_buscar_archivos_avisa_carpeta_faltante(tmp_path, monkeypatch):
    carpeta_faltante = tmp_path / "no_existe"
    monkeypatch.setattr(basic_tools.config, "ALLOWED_SEARCH_DIRS", [str(carpeta_faltante)])

    resultado = basic_tools.buscar_archivos("algo")

    assert str(carpeta_faltante) in resultado


def test_buscar_archivos_texto_vacio_no_busca():
    resultado = basic_tools.buscar_archivos("   ")

    assert "dime qué archivo" in resultado.lower()


def test_responder_pregunta_predefinida_nombre():
    resultado = basic_tools.responder_pregunta("¿cómo te llamas?")

    assert resultado == "Me llamo Jarvis."


def test_responder_pregunta_predefinida_creador():
    resultado = basic_tools.responder_pregunta("¿quién te hizo?")

    assert "Javier" in resultado


def test_responder_pregunta_calculo_simple():
    resultado = basic_tools.responder_pregunta("cuánto es 2 + 2")

    assert resultado == "El resultado es 4."


def test_responder_pregunta_calculo_con_decimales():
    resultado = basic_tools.responder_pregunta("cuánto es 10 / 4")

    assert resultado == "El resultado es 2.5."


def test_responder_pregunta_no_reconocida():
    resultado = basic_tools.responder_pregunta("cuéntame un chiste")

    assert "no sé responder" in resultado.lower()


def test_responder_pregunta_no_ejecuta_codigo_arbitrario():
    # __import__('os') no es aritmética -- debe rechazarse, nunca ejecutarse.
    resultado = basic_tools.responder_pregunta("cuánto es __import__('os')")

    assert "no sé responder" in resultado.lower()
