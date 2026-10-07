import numpy as np


class LaTeXRenderer:
    """Convierte matrices numéricas de NumPy a expresiones formateadas en LaTeX."""

    @staticmethod
    def matriz_a_latex(matriz: np.ndarray, nombre: str = "R") -> str:
        """
        Convierte una matriz bidimensional a un entorno bmatrix de LaTeX.
        Ejemplo: \\mathbf{R} = \begin{bmatrix} 10.00 & -5.00 \\ -5.00 & 15.00 \\end{bmatrix}
        """
        filas = []
        for fila in matriz:
            filas.append(" & ".join(f"{val:.2f}" for val in fila))
        cuerpo_matriz = r" \\ ".join(filas)

        return (
            rf"\mathbf{{{nombre}}} = \begin{{bmatrix}} {cuerpo_matriz} \end{{bmatrix}}"
        )
