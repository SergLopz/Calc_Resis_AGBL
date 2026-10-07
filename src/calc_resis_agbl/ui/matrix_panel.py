from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class MatrixPanel(QWidget):
    """Panel para la renderización de matrices matriciales formateadas en LaTeX."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 2), facecolor="#252526")
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def mostrar_ecuacion_latex(self, latex_str: str):
        """Renderiza una expresión matemática formateada en LaTeX en el panel."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis("off")
        ax.text(
            0.5,
            0.5,
            f"${latex_str}$",
            color="white",
            fontsize=14,
            ha="center",
            va="center",
        )
        self.canvas.draw()
