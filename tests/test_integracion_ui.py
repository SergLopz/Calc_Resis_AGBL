import pytest
from PyQt6.QtCore import QPointF

from calc_resis_agbl.core.mesh_solver import MeshSolver
from calc_resis_agbl.core.nodal_solver import NodalSolver
from calc_resis_agbl.ui.canvas import CircuitCanvas


def _lazo_cerrado(canvas: CircuitCanvas) -> None:
    """Crea un lazo rectangular V1 + 3 resistencias y marca tierra."""
    canvas.agregar_fuente(12.0, QPointF(80, 0))
    r2 = canvas.agregar_resistencia(1000.0, QPointF(120, 40))
    r2.setRotation(90)
    canvas.agregar_resistencia(2000.0, QPointF(80, 80))
    r4 = canvas.agregar_resistencia(3000.0, QPointF(40, 40))
    r4.setRotation(90)
    canvas._aplicar_iman_y_cables()
    canvas.marcar_tierra_en(QPointF(120, 0))


def _por_id(componentes):
    return {r["id"]: r for r in componentes}


def test_tierra_renombra_nodo_a_cero(qapp):
    canvas = CircuitCanvas()
    _lazo_cerrado(canvas)
    comps = canvas.construir_componentes_modelo()
    nodos = []
    for c in comps:
        nodos.extend(
            [
                getattr(c, "nodo_a", getattr(c, "nodo_positivo", None)),
                getattr(c, "nodo_b", getattr(c, "nodo_negativo", None)),
            ]
        )
    assert "0" in nodos


def test_metodos_coinciden_desde_el_lienzo(qapp):
    canvas = CircuitCanvas()
    _lazo_cerrado(canvas)
    comps = canvas.construir_componentes_modelo()
    mallas = _por_id(MeshSolver().resolver(comps)["componentes"])
    nodal = _por_id(NodalSolver().resolver(comps)["componentes"])
    for cid in mallas:
        assert mallas[cid]["corriente"] == pytest.approx(
            nodal[cid]["corriente"], abs=1e-9
        )


def test_corriente_del_lazo_es_correcta(qapp):
    canvas = CircuitCanvas()
    _lazo_cerrado(canvas)
    comps = canvas.construir_componentes_modelo()
    mallas = _por_id(MeshSolver().resolver(comps)["componentes"])
    # V=12, R_total=1000+2000+3000=6000 -> |I| = 2 mA en todas las ramas.
    for r in mallas.values():
        assert abs(r["corriente"]) == pytest.approx(2e-3, rel=1e-6)


def test_ley_de_tensiones_de_kirchhoff_desde_el_lienzo(qapp):
    canvas = CircuitCanvas()
    _lazo_cerrado(canvas)
    comps = canvas.construir_componentes_modelo()
    mallas = _por_id(MeshSolver().resolver(comps)["componentes"])

    suma_resistencias = 0.0
    fuente = 0.0
    for r in mallas.values():
        if r["tipo"] == "R":
            suma_resistencias += abs(r["voltaje"])
        else:
            fuente = abs(r["voltaje"])

    # La suma de caídas resistivas debe igualar el voltaje de la fuente (LVK).
    assert suma_resistencias == pytest.approx(fuente, rel=1e-9)
