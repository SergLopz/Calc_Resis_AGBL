import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class MatrixPanel(QWidget):
    """
    Panel que dibuja sistemas lineales M·x = b de forma manual (corchetes +
    entradas de texto). Se evita el entorno 'matrix' de LaTeX porque el motor
    mathtext de matplotlib no lo soporta.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(6, 2.4), facecolor="#252526")
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def mostrar_mensaje(self, texto: str) -> None:
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.5, texto, color="#CCCCCC", fontsize=11, ha="center", va="center")
        self.canvas.draw()

    def mostrar_sistema(
        self,
        matriz: np.ndarray,
        incognitas: list[str],
        lado_derecho: np.ndarray,
        titulo: str = "",
        decimales: int = 2,
    ) -> None:
        """Dibuja el sistema [M]·[x] = [b] con corchetes y entradas alineadas."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis("off")
        if titulo:
            ax.set_title(titulo, color="#8AB4F8", fontsize=10)

        matriz = np.atleast_2d(np.asarray(matriz, dtype=float))
        rhs = np.asarray(lado_derecho, dtype=float).reshape(-1, 1)
        x_col = [[s] for s in incognitas]

        self._dibujar_matriz(ax, matriz, x_inicial=0.08, decimales=decimales)
        ax.text(0.42, 0.5, r"$\cdot$".replace("$", ""), color="white",
                fontsize=18, ha="center", va="center")
        self._dibujar_matriz(ax, x_col, x_inicial=0.46, decimales=None)
        ax.text(0.62, 0.5, "=", color="white", fontsize=16, ha="center", va="center")
        self._dibujar_matriz(ax, rhs, x_inicial=0.68, decimales=decimales)
        self.canvas.draw()

    def _dibujar_matriz(
        self,
        ax,
        valores: list[list],
        x_inicial: float,
        decimales: int | None,
    ) -> None:
        """Dibuja una matriz con corchetes; si decimales es None, es texto (incógnitas)."""
        filas = len(valores)
        ancho = 0.14
        alto_total = 0.7

        def texto(v):
            if decimales is None:
                return str(v)
            return f"{float(v):.{decimales}f}"

        # Corchetes
        for lado, x in (("izq", x_inicial), ("der", x_inicial + ancho)):
            ax.plot([x, x], [0.15, 0.15 + alto_total], color="white", lw=1.5)
            signo = 1 if lado == "izq" else -1
            ax.plot([x, x + signo * 0.015], [0.15, 0.15], color="white", lw=1.5)
            ax.plot(
                [x, x + signo * 0.015],
                [0.15 + alto_total, 0.15 + alto_total],
                color="white",
                lw=1.5,
            )

        for i, fila in enumerate(valores):
            y = 0.15 + alto_total * (1 - (i + 0.5) / filas)
            for j, valor in enumerate(fila):
                x = x_inicial + 0.02 + j * (ancho - 0.04) / max(1, len(fila))
                ax.text(x + 0.05, y, texto(valor), color="white",
                        fontsize=11, ha="center", va="center")

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
