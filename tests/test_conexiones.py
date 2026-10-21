import pytest
from PyQt6.QtCore import QPointF

from calc_resis_agbl.core.mesh_solver import MeshSolver
from calc_resis_agbl.core.nodal_solver import NodalSolver
from calc_resis_agbl.ui.canvas import CircuitCanvas


def _por_id(componentes):
    return {r["id"]: r for r in componentes}


def _resolver(comps, solver):
    return solver().resolver(comps)["componentes"]


def test_modo_cable_conecta_terminales_separados(qapp):
    """Dos terminales en celdas distintas quedan en el mismo nodo si hay cable."""
    canvas = CircuitCanvas()
    v = canvas.agregar_fuente(12.0, QPointF(0, 0))
    r = canvas.agregar_resistencia(1000.0, QPointF(400, 0))
    # Cable entre el terminal negativo de V (idx 1) y el terminal a de R (idx 0).
    canvas._agregar_conexion((v, 1), (r, 0))
    canvas.marcar_tierra_en(QPointF(0, 0))

    comps = canvas.construir_componentes_modelo()
    fuente = next(c for c in comps if c.tipo == "V")
    resistencia = next(c for c in comps if c.tipo == "R")
    assert fuente.nodo_negativo == resistencia.nodo_a


def test_circuito_del_usuario_mallas_y_nodal(qapp):
    """
    V=12V en serie con R1=1k, luego el paralelo R2||R3 (=500||500=250).
    GND en el nodo inferior (negativo de la fuente y de R2/R3).
    Cables explícitos entre terminales separados.
    R_total = 1250 -> I = 9.6 mA, V_R1 = 9.6 V, V_paralelo = 2.4 V.
    """
    canvas = CircuitCanvas()
    fuente = canvas.agregar_fuente(12.0, QPointF(0, 0))          # + :a  - :b
    r1 = canvas.agregar_resistencia(1000.0, QPointF(400, 0))     # a:b
    r2 = canvas.agregar_resistencia(500.0, QPointF(800, -200))
    r3 = canvas.agregar_resistencia(500.0, QPointF(800, 200))

    # Nodo superior: + de la fuente -> R1.
    canvas._agregar_conexion((fuente, 0), (r1, 0))
    # Nodo intermedio: R1 -> R2 y R1 -> R3 (paralelo).
    canvas._agregar_conexion((r1, 1), (r2, 0))
    canvas._agregar_conexion((r1, 1), (r3, 0))
    # Nodo inferior (tierra): - de la fuente -> R2 y - de la fuente -> R3.
    canvas._agregar_conexion((fuente, 1), (r2, 1))
    canvas._agregar_conexion((fuente, 1), (r3, 1))
    # GND sobre el terminal negativo de la fuente (nodo inferior).
    canvas.marcar_tierra_en(fuente.terminales_escena()[1])

    comps = canvas.construir_componentes_modelo()
    mallas = _por_id(_resolver(comps, MeshSolver))
    nodal = _por_id(_resolver(comps, NodalSolver))

    # Ambas ramas del paralelo deben llevar la misma corriente.
    assert abs(mallas["R2"]["corriente"]) == pytest.approx(
        abs(mallas["R3"]["corriente"]), rel=1e-9
    )
    # Corriente total ~ 9.6 mA por R1 y por la fuente.
    assert abs(mallas["R1"]["corriente"]) == pytest.approx(9.6e-3, rel=1e-6)
    assert abs(mallas["V1"]["corriente"]) == pytest.approx(9.6e-3, rel=1e-6)    # V_R1 = 9.6 V ; V_paralelo = 2.4 V.
    assert abs(mallas["R1"]["voltaje"]) == pytest.approx(9.6, rel=1e-6)
    assert abs(mallas["R2"]["voltaje"]) == pytest.approx(2.4, rel=1e-6)
    assert abs(mallas["R3"]["voltaje"]) == pytest.approx(2.4, rel=1e-6)

    # Mallas ≡ Nodal.
    for cid in mallas:
        assert mallas[cid]["corriente"] == pytest.approx(
            nodal[cid]["corriente"], abs=1e-9
        )


def test_borrar_cables_elimina_conexiones(qapp):
    canvas = CircuitCanvas()
    v = canvas.agregar_fuente(12.0, QPointF(0, 0))
    r = canvas.agregar_resistencia(1000.0, QPointF(400, 0))
    canvas._agregar_conexion((v, 1), (r, 0))
    assert len(canvas._conexiones) == 1

    canvas.borrar_todos_los_cables()
    assert canvas._conexiones == []

    comps = canvas.construir_componentes_modelo()
    fuente = next(c for c in comps if c.tipo == "V")
    resistencia = next(c for c in comps if c.tipo == "R")
    # Sin cable, los terminales ya no comparten nodo.
    assert fuente.nodo_negativo != resistencia.nodo_a


def test_borrar_componente_elimina_sus_cables(qapp):
    canvas = CircuitCanvas()
    v = canvas.agregar_fuente(12.0, QPointF(0, 0))
    r = canvas.agregar_resistencia(1000.0, QPointF(400, 0))
    canvas._agregar_conexion((v, 1), (r, 0))

    canvas.scene.removeItem(r)
    canvas._reconstruir_cables()
    assert canvas._conexiones == []


def test_no_duplica_conexiones(qapp):
    canvas = CircuitCanvas()
    v = canvas.agregar_fuente(12.0, QPointF(0, 0))
    r = canvas.agregar_resistencia(1000.0, QPointF(400, 0))
    canvas._agregar_conexion((v, 1), (r, 0))
    canvas._agregar_conexion((r, 0), (v, 1))
    assert len(canvas._conexiones) == 1
