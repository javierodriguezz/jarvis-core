"""
Pruebas del modo manos libres de main.py (Fase 7).

No se abre el micrófono ni se carga ningún modelo: se reemplazan el detector,
la grabación/transcripción, la voz y la tubería de procesamiento por dobles.
Lo que se verifica aquí es el orden y las condiciones del bucle, no el audio.
"""

import pytest

import main


class _DetectorFalso:
    """Detecta la palabra de activación 'veces' veces y luego corta con Ctrl+C."""

    def __init__(self, veces):
        self.veces = veces
        self.llamadas = 0

    def __call__(self):
        self.llamadas += 1
        if self.llamadas > self.veces:
            # Simula el Ctrl+C con el que el usuario sale del modo escucha.
            raise KeyboardInterrupt
        return None


@pytest.fixture
def espia(monkeypatch):
    """Enchufa dobles a todo lo que toca el bucle y registra lo que va pasando."""
    registro = {"dicho": [], "procesado": [], "grabaciones": []}

    monkeypatch.setattr(main, "hablar", lambda texto: registro["dicho"].append(texto))
    monkeypatch.setattr(
        main, "procesar_texto", lambda texto: registro["procesado"].append(texto)
    )
    return registro


def test_modo_escucha_saluda_graba_y_procesa_lo_que_oyo(monkeypatch, espia):
    monkeypatch.setattr(main.detector, "esperar_palabra_activacion", _DetectorFalso(1))
    monkeypatch.setattr(
        main,
        "escuchar_una_vez",
        lambda cuenta_regresiva: espia["grabaciones"].append(cuenta_regresiva)
        or "qué hora es",
    )

    main.modo_escucha()

    assert espia["dicho"] == ["¿Sí?"]
    assert espia["procesado"] == ["qué hora es"]


def test_modo_escucha_graba_sin_cuenta_regresiva(monkeypatch, espia):
    # Tras decir "hey Jarvis" el usuario ya viene hablando: no se puede esperar.
    monkeypatch.setattr(main.detector, "esperar_palabra_activacion", _DetectorFalso(1))
    monkeypatch.setattr(
        main,
        "escuchar_una_vez",
        lambda cuenta_regresiva: espia["grabaciones"].append(cuenta_regresiva) or "hola",
    )

    main.modo_escucha()

    assert espia["grabaciones"] == [False]


def test_modo_escucha_no_procesa_nada_si_no_se_entendio_audio(monkeypatch, espia):
    monkeypatch.setattr(main.detector, "esperar_palabra_activacion", _DetectorFalso(1))
    monkeypatch.setattr(main, "escuchar_una_vez", lambda cuenta_regresiva: "")

    main.modo_escucha()

    assert espia["procesado"] == []
    assert espia["dicho"] == ["¿Sí?", "No escuché nada."]


def test_modo_escucha_vuelve_a_esperar_la_palabra_tras_cada_orden(monkeypatch, espia):
    # Dos activaciones seguidas: el bucle no se queda atorado tras la primera.
    detector_falso = _DetectorFalso(2)
    monkeypatch.setattr(main.detector, "esperar_palabra_activacion", detector_falso)
    monkeypatch.setattr(main, "escuchar_una_vez", lambda cuenta_regresiva: "hola")

    main.modo_escucha()

    assert espia["procesado"] == ["hola", "hola"]
    # La tercera llamada es la que levantó el KeyboardInterrupt de salida.
    assert detector_falso.llamadas == 3


def test_modo_escucha_sale_limpio_con_ctrl_c(monkeypatch, espia):
    monkeypatch.setattr(main.detector, "esperar_palabra_activacion", _DetectorFalso(0))
    monkeypatch.setattr(main, "escuchar_una_vez", lambda cuenta_regresiva: "hola")

    # No debe propagar el KeyboardInterrupt: regresa al prompt de texto.
    main.modo_escucha()

    assert espia["procesado"] == []
