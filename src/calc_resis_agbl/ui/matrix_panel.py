import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget


class MatrixPanel(QWidget):
    """
    Panel que dibuja sistemas lineales en formato matricial apilado:

        R = [ ... ]
        I = [ ... ]
        V = [ ... ]

    Cada matriz se dibuja manualmente (corchetes + entradas alineadas) porque
    el motor mathtext de matplotlib no soporta el entorno 'matrix' de LaTeX.
    El panel incluye un área de desplazamiento para matrices grandes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.figure = Figure(figsize=(6, 3), facecolor="#252526")
        self.canvas = FigureCanvas(self.figure)
        self.scroll.setWidget(self.canvas)
        self.layout.addWidget(self.scroll)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def mostrar_mensaje(self, texto: str) -> None:
        self.figure.clear()
        self.figure.set_size_inches(6, 2)
        ax = self.figure.add_subplot(111)
        ax.axis("off")
        ax.text(
            0.5,
            0.5,
            texto,
            color="#CCCCCC",
            fontsize=11,
            ha="center",
            va="center",
            wrap=True,
        )
        self._ajustar_tamano()
        self.canvas.draw()

    def mostrar_sistema(
        self,
        matriz: np.ndarray,
        incognitas: list[str],
        lado_derecho: np.ndarray,
        titulo: str = "",
        decimales: int = 2,
        solucion: np.ndarray | None = None,
        nombres: tuple[str, str, str] = ("R (Ω)", "I (A)", "V (V)"),
        etiquetas_filas: list[str] | None = None,
        etiquetas_columnas: list[str] | None = None,
        unidad_solucion: str = "A",
    ) -> None:
        """
        Dibuja las tres matrices del sistema, una debajo de otra.

        ``nombres`` permite adaptar los títulos (por ejemplo, A/x/b en nodal).
        ``etiquetas_filas`` y ``etiquetas_columnas`` rotulan las mallas; si no
        se indican, se usan M1, M2...
        """
        matriz = np.atleast_2d(np.asarray(matriz, dtype=float))
        rhs = np.asarray(lado_derecho, dtype=float).reshape(-1, 1)
        filas = matriz.shape[0]
        if filas == 0:
            return

        etiquetas_filas = etiquetas_filas or [f"M{i + 1}" for i in range(filas)]
        etiquetas_columnas = etiquetas_columnas or etiquetas_filas
        vector_incognitas = [[etiqueta] for etiqueta in incognitas]
        vector_valores = rhs.tolist()

        self.figure.clear()
        alto = max(3.0, 0.32 * (3 * filas) + 1.3)
        ancho = max(6.0, 0.8 * filas + 2.5)
        self.figure.set_size_inches(ancho, alto)

        rejilla = self.figure.add_gridspec(
            4,
            1,
            height_ratios=[max(filas, 1), max(filas, 1), max(filas, 1), 0.9],
            hspace=0.6,
        )
        self.figure.subplots_adjust(top=0.90 if titulo else 0.98, bottom=0.02)
        if titulo:
            self.figure.suptitle(titulo, color="#8AB4F8", fontsize=10, y=0.995)

        self._dibujar_bloque(
            self.figure.add_subplot(rejilla[0]),
            matriz.tolist(),
            nombres[0],
            etiquetas_filas,
            etiquetas_columnas,
            decimales,
        )
        self._dibujar_bloque(
            self.figure.add_subplot(rejilla[1]),
            vector_incognitas,
            nombres[1],
            etiquetas_filas,
            None,
            None,
        )
        self._dibujar_bloque(
            self.figure.add_subplot(rejilla[2]),
            vector_valores,
            nombres[2],
            etiquetas_filas,
            None,
            decimales,
        )
        self._dibujar_solucion(
            self.figure.add_subplot(rejilla[3]),
            incognitas,
            solucion,
            unidad_solucion,
        )
        self._ajustar_tamano()
        self.canvas.draw()

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------
    @staticmethod
    def _texto_celda(valor, decimales: int | None) -> str:
        if isinstance(valor, str):
            return valor
        if decimales is None:
            return str(valor)
        return f"{float(valor):.{decimales}f}"

    @staticmethod
    def _tamano_fuente(filas: int, max_caracteres: int) -> int:
        if max_caracteres <= 4:
            fuente = 12
        elif max_caracteres <= 7:
            fuente = 10
        elif max_caracteres <= 12:
            fuente = 8
        else:
            fuente = 6
        if filas > 8:
            fuente = min(fuente, 8)
        if filas > 14:
            fuente = min(fuente, 6)
        return fuente

    def _dibujar_bloque(
        self,
        ax,
        valores: list[list],
        titulo: str,
        etiquetas_filas: list[str],
        etiquetas_columnas: list[str] | None,
        decimales: int | None,
    ) -> None:
        """Dibuja una matriz con corchetes, título y etiquetas de fila/columna."""
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        filas = len(valores)
        columnas = max(1, max(len(fila) for fila in valores))
        textos = [
            [
                self._texto_celda(fila[col] if col < len(fila) else "", decimales)
                for col in range(columnas)
            ]
            for fila in valores
        ]
        max_len_col = [
            max(len(textos[fila][col]) for fila in range(filas))
            for col in range(columnas)
        ]
        fuente = self._tamano_fuente(filas, max(max_len_col, default=1))

        margen_izq = 0.20 if etiquetas_filas else 0.04
        margen_der = 0.03
        margen_sup = 0.34 if etiquetas_columnas else 0.16
        margen_inf = 0.06
        x_ini, x_fin = margen_izq, 1 - margen_der
        y_ini, y_fin = margen_inf, 1 - margen_sup

        ax.text(
            0.01,
            0.99,
            titulo,
            ha="left",
            va="top",
            color="#8AB4F8",
            fontsize=10,
            fontweight="bold",
        )

        disponible = x_fin - x_ini
        pesos = [max(1, max_len_col[col]) + 1.2 for col in range(columnas)]
        total_peso = sum(pesos)
        # Ancho proporcional al contenido: una columna no debe ocupar todo el
        # panel, y una matriz grande se limita al ancho disponible.
        ancho_matriz = min(disponible, max(0.12, total_peso * 0.024))
        x_fin = x_ini + ancho_matriz

        pad = min(0.02, ancho_matriz * 0.08)
        tick = min(0.015, ancho_matriz * 0.08)
        x_izq = x_ini + pad
        x_der = x_fin - pad
        for x, signo in ((x_izq, 1), (x_der, -1)):
            ax.plot([x, x], [y_ini, y_fin], color="white", lw=1.5)
            ax.plot([x, x + signo * tick], [y_ini, y_ini], color="white", lw=1.5)
            ax.plot([x, x + signo * tick], [y_fin, y_fin], color="white", lw=1.5)

        ancho_util = (x_der - tick) - (x_izq + tick)
        anchos = [ancho_util * peso / total_peso for peso in pesos]
        x_celda_ini = x_izq + tick

        for fila in range(filas):
            y = y_fin - (y_fin - y_ini) * (fila + 0.5) / filas
            if fila < len(etiquetas_filas):
                ax.text(
                    x_izq - 0.02,
                    y,
                    etiquetas_filas[fila],
                    ha="right",
                    va="center",
                    color="#CCCCCC",
                    fontsize=max(6, fuente - 1),
                )
            for col in range(columnas):
                x = x_celda_ini + sum(anchos[:col]) + anchos[col] / 2
                ax.text(
                    x,
                    y,
                    textos[fila][col],
                    color="white",
                    fontsize=fuente,
                    ha="center",
                    va="center",
                )

        if etiquetas_columnas:
            for col in range(min(columnas, len(etiquetas_columnas))):
                x = x_celda_ini + sum(anchos[:col]) + anchos[col] / 2
                ax.text(
                    x,
                    y_fin + 0.02,
                    etiquetas_columnas[col],
                    ha="center",
                    va="bottom",
                    color="#8AB4F8",
                    fontsize=max(6, fuente - 1),
                )

    @staticmethod
    def _dibujar_solucion(
        ax,
        incognitas: list[str],
        solucion: np.ndarray | None,
        unidad: str,
    ) -> None:
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        if solucion is None:
            return

        valores = np.asarray(solucion, dtype=float).reshape(-1)
        partes = []
        for etiqueta, valor in zip(incognitas, valores):
            texto = f"{etiqueta} = {valor:.6g}"
            if unidad:
                texto += f" {unidad}"
            partes.append(texto)
        ax.text(
            0.01,
            0.5,
            "Solución: " + "   ·   ".join(partes),
            ha="left",
            va="center",
            color="#00FFCC",
            fontsize=9,
        )

    def _ajustar_tamano(self) -> None:
        """Ajusta el tamaño mínimo del lienzo para que aparezcan las barras."""
        dpi = self.figure.dpi
        ancho = int(self.figure.get_figwidth() * dpi)
        alto = int(self.figure.get_figheight() * dpi)
        self.canvas.setMinimumSize(ancho, alto)
        self.canvas.updateGeometry()
