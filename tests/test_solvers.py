import pytest

from calc_resis_agbl.core.mesh_solver import MeshSolver
from calc_resis_agbl.core.nodal_solver import NodalSolver
from calc_resis_agbl.models.componentes import FuenteDC, Resistencia


def circuito_divisor():
    """Divisor de tensión simple: V1=12V, R1=1000Ω serie, R2=2000Ω a tierra."""
    return [
        FuenteDC("V1", 12.0, "1", "0"),
        Resistencia("R1", 1000.0, "1", "2"),
        Resistencia("R2", 2000.0, "2", "0"),
    ]


def circuito_dos_mallas():
    """Dos mallas independientes: R2 es la rama compartida entre ambas."""
    return [
        FuenteDC("V1", 12.0, "1", "0"),
        Resistencia("R1", 1000.0, "1", "2"),
        Resistencia("R2", 2000.0, "2", "0"),
        Resistencia("R3", 1000.0, "2", "3"),
        Resistencia("R4", 3000.0, "3", "0"),
    ]


def por_id(resultados):
    return {r["id"]: r for r in resultados}


def test_divisor_tension_mallas():
    resultado = MeshSolver().resolver(circuito_divisor())
    comp = por_id(resultado["componentes"])
    # Corriente total = 12 / 3000 = 4 mA
    assert comp["R1"]["corriente"] == pytest.approx(4e-3, rel=1e-6)
    assert comp["R1"]["voltaje"] == pytest.approx(4.0, rel=1e-6)
    assert comp["R2"]["voltaje"] == pytest.approx(8.0, rel=1e-6)


def test_mallas_y_nodal_coinciden():
    componentes = circuito_dos_mallas()
    mallas = por_id(MeshSolver().resolver(componentes)["componentes"])
    nodal = por_id(NodalSolver().resolver(componentes)["componentes"])
    for cid in mallas:
        assert mallas[cid]["corriente"] == pytest.approx(nodal[cid]["corriente"], abs=1e-9)
        assert mallas[cid]["voltaje"] == pytest.approx(nodal[cid]["voltaje"], abs=1e-9)


def test_potencia_disipada_positiva_en_resistencias():
    resultado = MeshSolver().resolver(circuito_divisor())
    comp = por_id(resultado["componentes"])
    assert comp["R1"]["potencia"] > 0
    assert comp["R2"]["potencia"] > 0
