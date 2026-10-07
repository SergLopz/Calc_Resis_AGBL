import numpy as np

from calc_resis_agbl.core.solver import CircuitSolver


def test_resolucion_mallas_simple():
    """Valida la resolución de un sistema matricial 2x2 conocido."""
    R = np.array([[10.0, -5.0], [-5.0, 15.0]])
    V = np.array([12.0, 0.0])

    I_esperado = np.array([1.44, 0.48])  # Solución exacta teórica
    I_calculado = CircuitSolver.resolver_sistema_mallas(R, V)

    np.testing.assert_almost_equal(I_calculado, I_esperado, decimal=2)
