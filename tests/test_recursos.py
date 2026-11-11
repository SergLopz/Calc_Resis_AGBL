from PyQt6.QtGui import QIcon

from calc_resis_agbl.ui.recursos import ruta_icono


def test_el_icono_existe_y_carga(qapp):
    ruta = ruta_icono()

    assert ruta.is_file()
    assert ruta.suffix.lower() == ".ico"

    icono = QIcon(str(ruta))
    assert not icono.isNull()
    assert not icono.pixmap(32, 32).isNull()
