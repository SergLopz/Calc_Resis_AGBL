"""Genera los iconos de la aplicación en varios formatos y resoluciones.

Uso:
    uv run python scripts/generar_iconos.py

El punto de partida es ``src/calc_resis_agbl/assets/icono_app.ico``. El script
lo vuelve cuadrado, conserva el color de fondo original y produce:

- ``icono_app.ico`` multirresolución para Windows y la barra de título.
- ``icono_app.png`` para Linux, documentación y futuros empaquetados.
- ``icono_app.icns`` para el bundle de macOS.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parents[1]
ASSETS = RAIZ / "src" / "calc_resis_agbl" / "assets"
FUENTE = ASSETS / "icono_app.ico"

TAMANOS_ICO = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def main() -> None:
    if not FUENTE.is_file():
        raise SystemExit(f"No se encontró el icono de origen: {FUENTE}")

    imagen = Image.open(FUENTE).convert("RGBA")
    lado = max(imagen.size)
    fondo = imagen.getpixel((0, 0))
    cuadrada = ImageOps.pad(imagen, (lado, lado), color=fondo, centering=(0.5, 0.5))

    cuadrada.save(FUENTE, format="ICO", sizes=TAMANOS_ICO)
    cuadrada.save(ASSETS / "icono_app.png", format="PNG")
    cuadrada.save(ASSETS / "icono_app.icns", format="ICNS")

    print(f"Origen: {imagen.size} -> cuadrado: {cuadrada.size}")
    print(f"ICO multirresolución: {FUENTE}")
    print(f"PNG: {ASSETS / 'icono_app.png'}")
    print(f"ICNS: {ASSETS / 'icono_app.icns'}")


if __name__ == "__main__":
    main()
