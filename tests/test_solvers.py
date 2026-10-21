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


def circuito_paralelo():
    """V=12V, R1=1k serie con el paralelo R2||R3 (500Ω cada una)."""
    return [
        FuenteDC("V1", 12.0, "0", "n1"),
        Resistencia("R1", 1000.0, "n1", "n2"),
        Resistencia("R2", 500.0, "n2", "0"),
        Resistencia("R3", 500.0, "n2", "0"),
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


def test_mallas_resuelve_paralelo_real():
    """R2||R3 = 250Ω; R_total = 1250Ω -> I_total = 9.6mA, V_R1 = 9.6V."""
    comp = por_id(MeshSolver().resolver(circuito_paralelo())["componentes"])
    assert abs(comp["R1"]["corriente"]) == pytest.approx(9.6e-3, rel=1e-6)
    assert abs(comp["R2"]["corriente"]) == pytest.approx(4.8e-3, rel=1e-6)
    assert abs(comp["R3"]["corriente"]) == pytest.approx(4.8e-3, rel=1e-6)
    assert abs(comp["R1"]["voltaje"]) == pytest.approx(9.6, rel=1e-6)
    assert abs(comp["R2"]["voltaje"]) == pytest.approx(2.4, rel=1e-6)
    assert abs(comp["R3"]["voltaje"]) == pytest.approx(2.4, rel=1e-6)


def test_paralelo_mallas_y_nodal_coinciden():
    componentes = circuito_paralelo()
    mallas = por_id(MeshSolver().resolver(componentes)["componentes"])
    nodal = por_id(NodalSolver().resolver(componentes)["componentes"])
    for cid in mallas:
        assert mallas[cid]["corriente"] == pytest.approx(
            nodal[cid]["corriente"], abs=1e-9
        )
        assert mallas[cid]["voltaje"] == pytest.approx(nodal[cid]["voltaje"], abs=1e-9)


def test_paralelo_no_muta_los_componentes_originales():
    componentes = circuito_paralelo()
    valores = {c.id: getattr(c, "valor_ohms", None) for c in componentes}
    MeshSolver().resolver(componentes)
    for c in componentes:
        if c.id in valores and valores[c.id] is not None:
            assert c.valor_ohms == valores[c.id]
