"""Rutas a recursos empaquetados con la aplicación."""

from __future__ import annotations

import sys
from pathlib import Path


def ruta_icono() -> Path:
    """
    Devuelve la ruta del icono de la aplicación.

    En desarrollo el icono vive junto al paquete. Dentro de un ejecutable de
    PyInstaller se busca en la carpeta temporal ``_MEIPASS``, donde se extraen
    los recursos declarados con ``--add-data``.
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "calc_resis_agbl" / "assets" / "icono_app.ico"
    return Path(__file__).resolve().parent.parent / "assets" / "icono_app.ico"
