import pytest
from PyQt6.QtCore import QPointF

from calc_resis_agbl.core.mesh_solver import MeshSolver
from calc_resis_agbl.core.nodal_solver import NodalSolver
from calc_resis_agbl.models.componentes import FuenteDC, Resistencia, Terminal
from calc_resis_agbl.ui.canvas import CircuitCanvas
from calc_resis_agbl.ui.main_window import MainWindow


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


# ----------------------------------------------------------------------
# Fase D: leyenda de mallas y etiquetas en la ventana principal
# ----------------------------------------------------------------------
def _textos_panel(ventana: MainWindow) -> list[str]:
    return [
        texto.get_text()
        for eje in ventana.matrix_panel.figure.axes
        for texto in eje.texts
    ]


def _circuito_con_paralelo() -> list[object]:
    """V1 + R1 en serie con el paralelo R2 || R3 (todas con geometría)."""
    posiciones = {"0": (0.0, 0.0), "n1": (0.0, 40.0), "n2": (40.0, 40.0)}

    def terminal(nodo):
        return Terminal(*posiciones[nodo])

    return [
        FuenteDC(
            "V1",
            12.0,
            "0",
            "n1",
            terminal_positivo=terminal("0"),
            terminal_negativo=terminal("n1"),
        ),
        Resistencia(
            "R1",
            1000.0,
            "n1",
            "n2",
            terminal_a=terminal("n1"),
            terminal_b=terminal("n2"),
        ),
        Resistencia(
            "R2",
            500.0,
            "n2",
            "0",
            terminal_a=terminal("n2"),
            terminal_b=terminal("0"),
        ),
        Resistencia(
            "R3",
            500.0,
            "n2",
            "0",
            terminal_a=terminal("n2"),
            terminal_b=terminal("0"),
        ),
    ]


def test_leyenda_mallas_muestra_id_sentido_y_componentes(qapp):
    canvas = CircuitCanvas()
    _lazo_cerrado(canvas)
    resultado = MeshSolver().resolver(canvas.construir_componentes_modelo())

    ventana = MainWindow()
    ventana._mostrar_leyenda_mallas(resultado)
    leyenda = ventana.leyenda_mallas.toPlainText()

    assert "M1" in leyenda
    assert "horario" in leyenda
    for comp_id in ("V1", "R1", "R2", "R3"):
        assert comp_id in leyenda


def test_leyenda_mallas_anota_el_equivalente_de_paralelos(qapp):
    resultado = MeshSolver().resolver(_circuito_con_paralelo())

    ventana = MainWindow()
    ventana._mostrar_leyenda_mallas(resultado)
    leyenda = ventana.leyenda_mallas.toPlainText()

    assert "R2 || R3 = 250 Ω" in leyenda


def test_leyenda_nodal_avisa_que_no_hay_mallas(qapp):
    ventana = MainWindow()
    ventana._mostrar_leyenda_nodal()

    assert "no usa mallas" in ventana.leyenda_mallas.toPlainText()


def test_matriz_de_mallas_usa_etiquetas_i_m(qapp):
    canvas = CircuitCanvas()
    _lazo_cerrado(canvas)
    resultado = MeshSolver().resolver(canvas.construir_componentes_modelo())

    ventana = MainWindow()
    ventana._mostrar_matriz_mallas(resultado)
    textos = _textos_panel(ventana)

    assert "R (Ω)" in textos
    assert "I (A)" in textos
    assert "V (V)" in textos
    assert "I_M1" in textos
    assert "M1" in textos


def test_matriz_nodal_usa_nombres_a_x_b(qapp):
    canvas = CircuitCanvas()
    _lazo_cerrado(canvas)
    resultado = NodalSolver().resolver(canvas.construir_componentes_modelo())

    ventana = MainWindow()
    ventana._mostrar_matriz_nodal(resultado)
    textos = _textos_panel(ventana)

    assert "A" in textos
    assert "x" in textos
    assert "b" in textos
    assert any(texto.startswith("Ec. ") for texto in textos)
