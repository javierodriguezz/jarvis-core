"""
Pruebas del logger (jarvis/utils/logger.py).
"""

import logging

from jarvis.utils import logger


def test_registrar_ejecucion_incluye_datos_clave(caplog):
    with caplog.at_level(logging.INFO):
        logger.registrar_ejecucion("decir_hora", {}, "Son las 10:00 del 01/01/2026")

    assert "decir_hora" in caplog.text
    assert "Son las 10:00 del 01/01/2026" in caplog.text
