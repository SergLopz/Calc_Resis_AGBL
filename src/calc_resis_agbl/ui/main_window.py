from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QSplitter

from calc_resis_agbl.ui.canvas import CircuitCanvas
from calc_resis_agbl.ui.matrix_panel import MatrixPanel


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación con layout responsive."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Visual de Circuitos - Grupo Juiciosos")
        self.resize(1200, 800)

        # Contenedor dividible (QSplitter) para mantener layout responsive
        splitter = QSplitter(Qt.Orientation.Vertical)

        self.canvas = CircuitCanvas(self)
        self.matrix_panel = MatrixPanel(self)

        splitter.addWidget(self.canvas)
        splitter.addWidget(self.matrix_panel)
        splitter.setSizes([600, 200])

        self.setCentralWidget(splitter)

        # Renderizado de prueba inicial
        self.matrix_panel.mostrar_ecuacion_latex(
            r"\mathbf{R} \cdot \mathbf{I} = \mathbf{V}"
        )
