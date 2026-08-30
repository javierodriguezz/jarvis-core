"""
Logging simple a archivo (data/jarvis.log).

Cada acción que el ejecutor corre debe quedar registrada aquí: qué
herramienta, con qué parámetros, si se confirmó, y el resultado.
"""

import logging

from config import DATA_DIR

DATA_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=DATA_DIR / "jarvis.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def registrar_ejecucion(tool_name: str, params: dict, resultado: str) -> None:
    """Escribe en el log una línea con la herramienta ejecutada, sus parámetros y el resultado."""
    logging.info("herramienta=%s params=%s resultado=%s", tool_name, params, resultado)
