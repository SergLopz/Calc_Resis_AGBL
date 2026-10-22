import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget

SIMBOLO_PRODUCTO = "\u00b7"  # "·" real (no LaTeX)


class MatrixPanel(QWidget):
    """
    Panel que dibuja sistemas lineales M·x = b (y opcionalmente la solución x)
    de forma manual: corchetes + entradas de texto alineadas en filas y columnas.

    Se evita el entorno 'matrix' de LaTeX porque el motor mathtext de matplotlib
    no lo soporta.
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
        solucion: np.ndarray | None = None,
    ) -> None:
        """
        Dibuja el sistema [M]·[x] = [b]. Si `solucion` no es None, añade en la
        misma figura la columna resultado [x] tras un '='.
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        if titulo:
            ax.set_title(titulo, color="#8AB4F8", fontsize=10)

        matriz = np.atleast_2d(np.asarray(matriz, dtype=float))
        rhs = np.asarray(lado_derecho, dtype=float).reshape(-1, 1)
        x_col = [[s] for s in incognitas]
        filas = matriz.shape[0]
        fuente = self._tamano_fuente(filas)

        # Cada bloque ocupa una fracción horizontal; se separa con símbolos.
        bloques: list[tuple[list[list], str | None, int]] = [
            (matriz.tolist(), None, decimales),
        ]
        separadores: list[str] = []
        bloques.append((x_col, None, None))
        separadores.append(SIMBOLO_PRODUCTO)
        bloques.append((rhs.tolist(), None, decimales))
        separadores.append("=")

        if solucion is not None:
            sol = np.asarray(solucion, dtype=float).reshape(-1, 1)
            bloques.append((sol.tolist(), None, decimales))
            separadores.append("=")

        self._disponer_bloques(ax, bloques, separadores, fuente)
        self.canvas.draw()

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------
    @staticmethod
    def _tamano_fuente(filas: int) -> int:
        if filas <= 2:
            return 12
        if filas <= 4:
            return 10
        if filas <= 6:
            return 9
        return 8

    def _disponer_bloques(
        self,
        ax,
        bloques: list[tuple[list[list], str | None, int | None]],
        separadores: list[str],
        fuente: int,
    ) -> None:
        """
        Reparte el ancho disponible entre las matrices (proporcional a su número
        de columnas) y coloca los separadores en los huecos entre bloques.
        """
        margen = 0.02
        ancho_sep = 0.05
        # Ancho proporcional: mínimo 1 columna; matrices de 1 columna pesan menos.
        pesos = [max(1, len(b[0][0])) + 0.6 for b in bloques]
        n_sep = len(separadores)
        ancho_disponible = 1.0 - 2 * margen - n_sep * ancho_sep
        total_peso = sum(pesos)
        anchos = [ancho_disponible * p / total_peso for p in pesos]

        x = margen
        for i, (valores, _, dec) in enumerate(bloques):
            self._dibujar_matriz(ax, valores, x, anchos[i], dec, fuente)
            x += anchos[i]
            if i < n_sep:
                ax.text(
                    x + ancho_sep / 2,
                    0.5,
                    separadores[i],
                    color="white",
                    fontsize=16,
                    ha="center",
                    va="center",
                )
                x += ancho_sep

    def _dibujar_matriz(
        self,
        ax,
        valores: list[list],
        x_ini: float,
        ancho: float,
        decimales: int | None,
        fuente: int,
    ) -> None:
        """Dibuja una matriz con corchetes y entradas alineadas en filas/columnas."""
        filas = len(valores)
        columnas = max(1, max(len(f) for f in valores))
        y_ini, y_fin = 0.12, 0.88

        def texto(v):
            if decimales is None:
                return str(v)
            return f"{float(v):.{decimales}f}"

        # Corchetes a los lados del bloque.
        pad_bracket = min(0.02, ancho * 0.12)
        x_izq = x_ini + pad_bracket
        x_der = x_ini + ancho - pad_bracket
        for x, signo in ((x_izq, 1), (x_der, -1)):
            ax.plot([x, x], [y_ini, y_fin], color="white", lw=1.5)
            tick = min(0.015, ancho * 0.1)
            ax.plot([x, x + signo * tick], [y_ini, y_ini], color="white", lw=1.5)
            ax.plot([x, x + signo * tick], [y_fin, y_fin], color="white", lw=1.5)

        # Centro horizontal disponible para las entradas.
        x_centro_ini = x_izq + tick
        x_centro_fin = x_der - tick
        ancho_col = (x_centro_fin - x_centro_ini) / columnas

        for i, fila in enumerate(valores):
            y = y_fin - (y_fin - y_ini) * (i + 0.5) / filas
            for j in range(columnas):
                valor = fila[j] if j < len(fila) else ""
                x = x_centro_ini + ancho_col * (j + 0.5)
                ax.text(
                    x,
                    y,
                    texto(valor),
                    color="white",
                    fontsize=fuente,
                    ha="center",
                    va="center",
                )
