"""Configuración global de Pytest.

Marca automáticamente cada prueba con la semana a la que pertenece
(según la carpeta tests/semanaN/), para poder filtrar con:  -m semana2
"""

import re

import pytest

_SEMANA = re.compile(r"semana(\d+)")


def pytest_collection_modifyitems(config, items):
    for item in items:
        match = _SEMANA.search(item.nodeid)
        if match:
            item.add_marker(getattr(pytest.mark, f"semana{match.group(1)}"))
