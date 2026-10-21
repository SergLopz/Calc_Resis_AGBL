import numpy as np


class LaTeXRenderer:
    """
    Convierte matrices y vectores numéricos a expresiones compatibles con el
    motor mathtext de matplotlib (usa \\left[\\begin{matrix}...\\end{matrix}\\right]
    en lugar de bmatrix, que mathtext no soporta).
    """

    @staticmethod
    def _matriz(matriz: np.ndarray, decimales: int) -> str:
        filas = [" & ".join(f"{v:.{decimales}f}" for v in fila) for fila in np.atleast_2d(matriz)]
        cuerpo = r" \\ ".join(filas)
        return rf"\left[\begin{{matrix}} {cuerpo} \end{{matrix}}\right]"

    @staticmethod
    def matriz_a_latex(matriz: np.ndarray, nombre: str = "R", decimales: int = 2) -> str:
        """Convierte una matriz bidimensional a notación matricial LaTeX."""
        return rf"\mathbf{{{nombre}}} = {LaTeXRenderer._matriz(matriz, decimales)}"

    @staticmethod
    def vector_a_latex(vector: np.ndarray, nombre: str = "V", decimales: int = 2) -> str:
        """Convierte un vector a una matriz columna LaTeX."""
        return rf"\mathbf{{{nombre}}} = {LaTeXRenderer._matriz(vector, decimales)}"

    @staticmethod
    def _columna(valores: list[str]) -> str:
        filas = r" \\ ".join(valores)
        return rf"\left[\begin{{matrix}} {filas} \end{{matrix}}\right]"

    @staticmethod
    def sistema_a_latex(
        matriz: np.ndarray,
        incognitas: list[str],
        lado_derecho: np.ndarray,
        decimales: int = 2,
    ) -> str:
        """Construye un sistema completo M · x = b con las incógnitas etiquetadas."""
        m = LaTeXRenderer._matriz(matriz, decimales)
        x = LaTeXRenderer._columna(incognitas)
        b = LaTeXRenderer._matriz(lado_derecho, decimales)
        return f"{m}{x} = {b}"
