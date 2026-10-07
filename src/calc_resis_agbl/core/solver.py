import numpy as np


class CircuitSolver:
    """Resuelve el sistema de mallas de Kirchhoff mediante álgebra lineal."""

    @staticmethod
    def resolver_sistema_mallas(
        matriz_r: np.ndarray, vector_v: np.ndarray
    ) -> np.ndarray:
        """
        Resuelve R * I = V.
        Retorna el vector de corrientes de malla I.
        """
        try:
            vector_i = np.linalg.solve(matriz_r, vector_v)
            return vector_i
        except np.linalg.LinAlgError:
            raise ValueError(
                "El sistema matricial es singular o el circuito no está cerrado correctamente."
            )


# Ejemplo rápido de uso para los practicantes:
if __name__ == "__main__":
    # Circuito simple de 2 mallas de prueba
    R = np.array([[10.0, -5.0], [-5.0, 15.0]])
    V = np.array([12.0, 0.0])

    I = CircuitSolver.resolver_sistema_mallas(R, V)
    print(f"Corrientes de malla calculadas: I1 = {I[0]:.3f} A, I2 = {I[1]:.3f} A")
