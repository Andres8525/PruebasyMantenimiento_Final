"""Regresión: el dashboard y el README solo pueden señalar archivos que existen.

Tras renombrar los componentes al dominio bancario, varias tarjetas de semana
seguían mostrando rutas antiguas (por ejemplo src/semana4/app.py). Estas pruebas
fallan si una ruta de código del dashboard o del README deja de existir.
"""

import re

import pytest

from dashboard.reports import ROOT, SEMANAS

RUTA_CODIGO = re.compile(r"\b(?:src|tests|scripts|dashboard|load)/[\w/.-]+\.py\b")


@pytest.mark.parametrize("clave", sorted(SEMANAS, key=int))
def test_tarjeta_de_semana_apunta_a_codigo_existente(clave):
    # Arrange
    modulo = SEMANAS[clave]["modulo"]

    # Act
    ruta = ROOT / modulo

    # Assert
    assert modulo.startswith(f"src/semana{clave}/"), modulo
    assert ruta.exists(), f"Semana {clave}: {modulo} no existe"


def test_readme_solo_menciona_archivos_existentes():
    # Arrange
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # Act
    faltantes = sorted({r for r in RUTA_CODIGO.findall(readme) if not (ROOT / r).exists()})

    # Assert
    assert faltantes == []
