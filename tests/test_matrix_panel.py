import numpy as np
from PyQt6.QtWidgets import QScrollArea

from calc_resis_agbl.ui.matrix_panel import MatrixPanel


def _textos(panel: MatrixPanel):
    return [texto.get_text() for eje in panel.figure.axes for texto in eje.texts]


def _eje_con(panel: MatrixPanel, texto: str):
    return next(
        eje
        for eje in panel.figure.axes
        if any(entrada.get_text() == texto for entrada in eje.texts)
    )


def test_formato_apilado_muestra_r_i_v(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(
        np.array([[1.0, 2.0], [3.0, 4.0]]),
        ["I_M1", "I_M2"],
        np.array([[5.0], [6.0]]),
    )
    textos = _textos(panel)

    assert "R (Ω)" in textos
    assert "I (A)" in textos
    assert "V (V)" in textos
    for valor in ("1.00", "2.00", "3.00", "4.00", "5.00", "6.00"):
        assert valor in textos


def test_etiquetas_de_malla_en_filas_y_columnas(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(
        np.array([[1.0, 0.0], [0.0, 1.0]]),
        ["I_M1", "I_M2"],
        np.zeros((2, 1)),
    )
    textos = _textos(panel)

    assert textos.count("M1") >= 3
    assert textos.count("M2") >= 3


def test_matriz_2x2_no_solapa_entradas(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(
        np.array([[1.0, 2.0], [3.0, 4.0]]),
        ["I_M1", "I_M2"],
        np.zeros((2, 1)),
    )
    eje = _eje_con(panel, "1.00")
    entradas = [
        texto
        for texto in eje.texts
        if texto.get_text() in {"1.00", "2.00", "3.00", "4.00"}
    ]

    xs = {round(texto.get_position()[0], 6) for texto in entradas}
    ys = {round(texto.get_position()[1], 6) for texto in entradas}
    assert len(xs) == 2, "las dos columnas deben tener x distinta (sin solape)"
    assert len(ys) == 2, "las dos filas deben tener y distinta"


def test_matriz_3x3_dibuja_nueve_entradas(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(
        np.arange(1, 10, dtype=float).reshape(3, 3),
        ["I_M1", "I_M2", "I_M3"],
        np.zeros((3, 1)),
    )
    eje = _eje_con(panel, "1.00")
    entradas = [
        texto
        for texto in eje.texts
        if texto.get_text().endswith(".00") and texto.get_text() != "0.00"
    ]

    assert len(entradas) == 9
    xs = {round(texto.get_position()[0], 6) for texto in entradas}
    ys = {round(texto.get_position()[1], 6) for texto in entradas}
    assert len(xs) == 3
    assert len(ys) == 3


def test_incognitas_aparecen_en_la_matriz_i(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(
        np.array([[1.0, 0.0], [0.0, 1.0]]),
        ["I_M1", "I_M2"],
        np.zeros((2, 1)),
    )
    textos = _textos(panel)

    assert "I_M1" in textos
    assert "I_M2" in textos


def test_sistema_1x1_sigue_funcionando(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(np.array([[6000.0]]), ["I_M1"], np.array([[12.0]]))
    textos = _textos(panel)

    assert "6000.00" in textos
    assert "12.00" in textos
    assert "I_M1" in textos


def test_solucion_aparece_como_texto(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(
        np.array([[1.0, 0.0], [0.0, 1.0]]),
        ["I_M1", "I_M2"],
        np.array([[1.5], [2.5]]),
        solucion=np.array([[0.004], [-0.002]]),
    )
    textos = _textos(panel)

    assert any("Solución" in texto for texto in textos)
    assert any("0.004" in texto for texto in textos)
    assert any("-0.002" in texto for texto in textos)


def test_matriz_grande_crece_y_tiene_area_de_desplazamiento(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(
        np.eye(8),
        [f"I_M{i}" for i in range(1, 9)],
        np.ones((8, 1)),
    )

    assert panel.figure.get_figheight() > 4
    assert panel.canvas.minimumHeight() > 0
    assert isinstance(panel.scroll, QScrollArea)


def test_nombres_personalizados_para_nodal(qapp):
    panel = MatrixPanel()
    panel.mostrar_sistema(
        np.array([[1.0]]),
        ["x1"],
        np.array([[1.0]]),
        nombres=("A", "x", "b"),
    )
    textos = _textos(panel)

    assert "A" in textos
    assert "x" in textos
    assert "b" in textos


def test_mostrar_mensaje(qapp):
    panel = MatrixPanel()
    panel.mostrar_mensaje("Circuito modificado. Presiona Resolver.")

    assert "Circuito modificado. Presiona Resolver." in _textos(panel)
