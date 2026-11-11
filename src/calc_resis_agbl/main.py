import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from calc_resis_agbl.ui.main_window import MainWindow
from calc_resis_agbl.ui.recursos import ruta_icono


def main():
    """Inicializa y ejecuta la aplicación de escritorio."""
    app = QApplication(sys.argv)
    app.setApplicationName("Calculadora de Circuitos Resistivos")
    app.setWindowIcon(QIcon(str(ruta_icono())))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
