import numpy as np

from calc_resis_agbl.ui.matrix_panel import SIMBOLO_PRODUCTO, MatrixPanel


def _textos(panel: MatrixPanel):
    ax = panel.figure.axes[0]
    return [t.get_text() for t in ax.texts]


def _posiciones_x(panel: MatrixPanel):
    ax = panel.figure.axes[0]
    return [round(t.get_position()[0], 6) for t in ax.texts]


def test_matriz_2x2_dibuja_cuatro_entradas(qapp):
    panel = MatrixPanel()
    matriz = np.array([[1.0, 2.0], [3.0, 4.0]])
    panel.mostrar_sistema(matriz, ["x1", "x2"], np.array([[5.0], [6.0]]))
    textos = _textos(panel)
    # Entradas de la matriz: 1,2,3,4
    for valor in ("1.00", "2.00", "3.00", "4.00"):
        assert valor in textos
    # Las cuatro entradas de la matriz deben tener 2 x distintas x 2 y.
    entradas = [
        t for t in panel.figure.axes[0].texts if t.get_text() in {"1.00", "2.00", "3.00", "4.00"}
    ]
    xs = {round(t.get_position()[0], 6) for t in entradas}
    ys = {round(t.get_position()[1], 6) for t in entradas}
    assert len(xs) == 2, "las dos columnas deben tener x distinta (sin solape)"
    assert len(ys) == 2, "las dos filas deben tener y distinta"


def test_matriz_3x3_dibuja_nueve_entradas(qapp):
    panel = MatrixPanel()
    matriz = np.arange(1, 10, dtype=float).reshape(3, 3)
    panel.mostrar_sistema(matriz, ["x1", "x2", "x3"], np.zeros((3, 1)))
    textos = _textos(panel)
    for valor in ("1.00", "5.00", "9.00"):
        assert valor in textos
    entradas = [
        t for t in panel.figure.axes[0].texts if t.get_text().endswith(".00")
        and float(t.get_text()) in set(matriz.flatten().tolist())
    ]
    assert len(entradas) == 9
    xs = {round(t.get_position()[0], 6) for t in entradas}
    ys = {round(t.get_position()[1], 6) for t in entradas}
    assert len(xs) == 3
    assert len(ys) == 3


def test_simbolo_producto_es_punto_unicode(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(np.array([[1.0]]), ["x1"], np.array([[2.0]]))
    textos = _textos(panel)
    assert SIMBOLO_PRODUCTO in textos
    assert r"\cdot" not in textos
    assert "cdot" not in textos


def test_sistema_1x1_sigue_funcionando(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(np.array([[6000.0]]), ["x1"], np.array([[12.0]]))
    textos = _textos(panel)
    assert "6000.00" in textos
    assert "12.00" in textos
    assert "x1" in textos


def test_muestra_columna_solucion(qapp):
    panel = MatrixPanel()
    solucion = np.array([[1.5], [2.5]])
    panel.mostrar_sistema(
        np.array([[1.0, 0.0], [0.0, 1.0]]),
        ["x1", "x2"],
        np.array([[1.5], [2.5]]),
        solucion=solucion,
    )
    textos = _textos(panel)
    assert "1.50" in textos
    assert "2.50" in textos


def test_incognitas_aparecen_como_columnas(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(np.array([[1.0, 0.0], [0.0, 1.0]]), ["x1", "x2"], np.zeros((2, 1)))
    textos = _textos(panel)
    assert "x1" in textos
    assert "x2" in textos
