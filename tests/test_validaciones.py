import pytest

from calc_resis_agbl.core.mesh_solver import MeshSolver
from calc_resis_agbl.core.nodal_solver import NodalSolver
from calc_resis_agbl.models.circuito import Circuito
from calc_resis_agbl.models.componentes import (
    MAX_FUENTES,
    MAX_RESISTENCIAS,
    NODO_REFERENCIA,
    CircuitoError,
    FuenteDC,
    Resistencia,
)


def _resistencia(i: int, nodo_a: str, nodo_b: str, valor: float = 1000.0) -> Resistencia:
    return Resistencia(id=f"R{i}", valor_ohms=valor, nodo_a=nodo_a, nodo_b=nodo_b)


def _fuente(i: int, nodo_pos: str, nodo_neg: str, valor: float = 12.0) -> FuenteDC:
    return FuenteDC(
        id=f"V{i}", valor_voltios=valor, nodo_positivo=nodo_pos, nodo_negativo=nodo_neg
    )


# ---------------------------------------------------------------------------
# Límites del grupo: 20 resistencias y 3 fuentes
# ---------------------------------------------------------------------------


def test_acepta_exactamente_20_resistencias():
    circuito = Circuito()
    for i in range(MAX_RESISTENCIAS):
        circuito.agregar_resistencia(_resistencia(i, "1", "2"))
    assert len(circuito.resistencias) == MAX_RESISTENCIAS


def test_rechaza_la_resistencia_21():
    circuito = Circuito()
    for i in range(MAX_RESISTENCIAS):
        circuito.agregar_resistencia(_resistencia(i, "1", "2"))
    with pytest.raises(CircuitoError, match="límite de 20 resistencias"):
        circuito.agregar_resistencia(_resistencia(99, "1", "2"))


def test_acepta_exactamente_3_fuentes():
    circuito = Circuito()
    for i in range(MAX_FUENTES):
        circuito.agregar_fuente(_fuente(i, "1", "2"))
    assert len(circuito.fuentes) == MAX_FUENTES


def test_rechaza_la_cuarta_fuente():
    circuito = Circuito()
    for i in range(MAX_FUENTES):
        circuito.agregar_fuente(_fuente(i, "1", "2"))
    with pytest.raises(CircuitoError, match="límite de 3 fuentes"):
        circuito.agregar_fuente(_fuente(99, "1", "2"))


# ---------------------------------------------------------------------------
# Errores de componentes inválidos
# ---------------------------------------------------------------------------


def test_resistencia_no_positiva_es_rechazada():
    circuito = Circuito()
    with pytest.raises(CircuitoError, match="mayor que 0"):
        circuito.agregar_resistencia(_resistencia(1, "1", "2", valor=0.0))


def test_identificador_duplicado_es_rechazado():
    circuito = Circuito()
    circuito.agregar_resistencia(_resistencia(1, "1", "2"))
    with pytest.raises(CircuitoError, match="ya existe"):
        circuito.agregar_resistencia(_resistencia(1, "1", "2"))


# ---------------------------------------------------------------------------
# Errores topológicos
# ---------------------------------------------------------------------------


def test_circuito_vacio_es_invalido():
    with pytest.raises(CircuitoError, match="al menos un componente"):
        Circuito().validar()


def test_circuito_sin_tierra_es_invalido():
    circuito = Circuito()
    circuito.agregar_resistencia(_resistencia(1, "1", "2"))
    with pytest.raises(CircuitoError, match="referencia"):
        circuito.validar()


def test_falta_de_nodo_de_referencia_se_detecta():
    circuito = Circuito()
    circuito.agregar_resistencia(_resistencia(1, "a", "b"))
    assert NODO_REFERENCIA not in circuito.nodos_usados()
    with pytest.raises(CircuitoError):
        circuito.validar()


def test_solvers_rechazan_grafo_desconectado():
    # Dos lazos independientes no unidos entre sí.
    componentes = [
        _fuente(1, "0", "1"),
        _resistencia(1, "1", "0", valor=1000.0),
        _resistencia(2, "2", "3", valor=1000.0),
        _resistencia(3, "3", "2", valor=1000.0),
    ]
    with pytest.raises(CircuitoError, match="desconectad"):
        MeshSolver().resolver(componentes)


def test_mesh_solver_rechaza_circuito_sin_mallas():
    # Una sola resistencia aislada no puede formar un lazo cerrado.
    with pytest.raises(CircuitoError):
        MeshSolver().resolver(
            [Resistencia(id="R1", valor_ohms=1000.0, nodo_a="0", nodo_b="1")]
        )


def test_nodal_solver_rechaza_circuito_sin_variables():
    with pytest.raises(CircuitoError):
        NodalSolver().resolver(
            [Resistencia(id="R1", valor_ohms=1000.0, nodo_a="0", nodo_b="0")]
        )
