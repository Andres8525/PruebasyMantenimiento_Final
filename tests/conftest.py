"""Configuración global de Pytest.

Marca automáticamente cada prueba con la semana a la que pertenece
(según la carpeta tests/semanaN/), para poder filtrar con:  -m semana2
Las pruebas del caso de uso de banca (tests/banca/) reciben el marcador "banca".
"""

import re

import pytest

_SEMANA = re.compile(r"semana(\d+)")


def pytest_collection_modifyitems(config, items):
    for item in items:
        match = _SEMANA.search(item.nodeid)
        if match:
            item.add_marker(getattr(pytest.mark, f"semana{match.group(1)}"))
        elif "tests/banca/" in item.nodeid.replace("\\", "/"):
            item.add_marker(pytest.mark.banca)
