from itertools import pairwise

import pytest

from calc_resis_agbl.core.graph_builder import GraphBuilder
from calc_resis_agbl.core.planar_meshes import extraer_mallas
from calc_resis_agbl.models.componentes import FuenteDC, Resistencia, Terminal


def _res(comp_id, nodo_a, nodo_b, posiciones, valor=100.0):
    return Resistencia(
        comp_id,
        valor,
        nodo_a,
        nodo_b,
        terminal_a=Terminal(*posiciones[nodo_a]),
        terminal_b=Terminal(*posiciones[nodo_b]),
    )


def _fuente(comp_id, nodo_a, nodo_b, posiciones, valor=12.0):
    return FuenteDC(
        comp_id,
        valor,
        nodo_a,
        nodo_b,
        terminal_positivo=Terminal(*posiciones[nodo_a]),
        terminal_negativo=Terminal(*posiciones[nodo_b]),
    )


def _circuito_dos_ventanas():
    posiciones = {
        "A": (0.0, 0.0),
        "B": (0.0, 40.0),
        "C": (40.0, 40.0),
        "D": (40.0, 0.0),
        "E": (80.0, 40.0),
        "F": (80.0, 0.0),
    }
    componentes = [
        _fuente("V1", "A", "B", posiciones),
        _res("R1", "B", "C", posiciones),
        _res("R2", "C", "D", posiciones),
        _res("R3", "D", "A", posiciones),
        _res("R4", "C", "E", posiciones),
        _res("R5", "E", "F", posiciones),
        _res("R6", "F", "D", posiciones),
    ]
    return posiciones, componentes


def _ids(malla):
    return {rama["elemento"].id for rama in malla["ramas"]}


def test_dos_ventanas_horizontales_orden_y_sentido_horario():
    _, componentes = _circuito_dos_ventanas()
    mallas = extraer_mallas(componentes)

    assert [malla["id"] for malla in mallas] == ["M1", "M2"]
    assert mallas[0]["centroide"][0] < mallas[1]["centroide"][0]
    assert all(malla["sentido"] == "horario" for malla in mallas)
    assert all(malla["area"] > 0 for malla in mallas)
    assert _ids(mallas[0]) == {"V1", "R1", "R2", "R3"}
    assert _ids(mallas[1]) == {"R2", "R4", "R5", "R6"}


def test_rama_compartida_se_recorre_en_sentidos_opuestos():
    _, componentes = _circuito_dos_ventanas()
    mallas = extraer_mallas(componentes)

    r2_m1 = next(rama for rama in mallas[0]["ramas"] if rama["elemento"].id == "R2")
    r2_m2 = next(rama for rama in mallas[1]["ramas"] if rama["elemento"].id == "R2")

    assert {r2_m1["origen"], r2_m1["destino"]} == {"C", "D"}
    assert r2_m1["origen"] == r2_m2["destino"]
    assert r2_m1["destino"] == r2_m2["origen"]


def test_una_sola_ventana_es_horaria_y_tiene_area_correcta():
    posiciones = {"A": (0.0, 0.0), "B": (0.0, 40.0), "C": (40.0, 40.0), "D": (40.0, 0.0)}
    componentes = [
        _res("R1", "A", "B", posiciones),
        _res("R2", "B", "C", posiciones),
        _res("R3", "C", "D", posiciones),
        _res("R4", "D", "A", posiciones),
    ]
    mallas = extraer_mallas(componentes)

    assert len(mallas) == 1
    assert mallas[0]["sentido"] == "horario"
    assert mallas[0]["area"] == pytest.approx(1600.0)


def test_grilla_bento_numera_desde_abajo_izquierda():
    xs = [0.0, 40.0, 80.0]
    ys = [0.0, 40.0, 80.0]
    posiciones = {f"N({x},{y})": (x, y) for x in xs for y in ys}
    componentes = []
    indice = 1
    for y in ys:
        for x0, x1 in pairwise(xs):
            componentes.append(
                _res(f"R{indice}", f"N({x0},{y})", f"N({x1},{y})", posiciones)
            )
            indice += 1
    for x in xs:
        for y0, y1 in pairwise(ys):
            componentes.append(
                _res(f"R{indice}", f"N({x},{y0})", f"N({x},{y1})", posiciones)
            )
            indice += 1

    mallas = extraer_mallas(componentes)

    assert [malla["id"] for malla in mallas] == ["M1", "M2", "M3", "M4"]
    centros = [malla["centroide"] for malla in mallas]
    assert centros[0] == pytest.approx((20.0, 60.0))
    assert centros[1] == pytest.approx((60.0, 60.0))
    assert centros[2] == pytest.approx((20.0, 20.0))
    assert centros[3] == pytest.approx((60.0, 20.0))


def test_puente_no_pertenece_a_ninguna_ventana():
    posiciones = {
        "A": (0.0, 0.0),
        "B": (0.0, 40.0),
        "C": (40.0, 40.0),
        "D": (40.0, 0.0),
        "E": (80.0, 40.0),
    }
    componentes = [
        _res("R1", "A", "B", posiciones),
        _res("R2", "B", "C", posiciones),
        _res("R3", "C", "D", posiciones),
        _res("R4", "D", "A", posiciones),
        _res("R5", "C", "E", posiciones),
    ]
    mallas = extraer_mallas(componentes)

    assert len(mallas) == 1
    assert "R5" not in _ids(mallas[0])


def test_ventanas_anidadas_se_separan_por_el_puente_y_por_area():
    posiciones = {
        "A": (0.0, 0.0),
        "B": (0.0, 80.0),
        "C": (80.0, 80.0),
        "D": (80.0, 0.0),
        "E": (20.0, 20.0),
        "F": (20.0, 60.0),
        "G": (60.0, 60.0),
        "H": (60.0, 20.0),
    }
    componentes = [
        _res("R1", "A", "B", posiciones),
        _res("R2", "B", "C", posiciones),
        _res("R3", "C", "D", posiciones),
        _res("R4", "D", "A", posiciones),
        _res("R5", "E", "F", posiciones),
        _res("R6", "F", "G", posiciones),
        _res("R7", "G", "H", posiciones),
        _res("R8", "H", "E", posiciones),
        _res("R9", "A", "E", posiciones),
    ]
    mallas = extraer_mallas(componentes)

    assert len(mallas) == 2
    assert mallas[0]["area"] < mallas[1]["area"]
    assert all(malla["sentido"] == "horario" for malla in mallas)
    for malla in mallas:
        assert "R9" not in _ids(malla)


def test_cruce_geometrico_usa_fallback_sin_fallar():
    posiciones = {
        "A": (0.0, 0.0),
        "B": (40.0, 0.0),
        "C": (40.0, 40.0),
        "D": (0.0, 40.0),
    }
    componentes = [
        _res("R1", "A", "B", posiciones),
        _res("R2", "B", "C", posiciones),
        _res("R3", "C", "D", posiciones),
        _res("R4", "D", "A", posiciones),
        _res("R5", "A", "C", posiciones),
        _res("R6", "B", "D", posiciones),
    ]
    mallas = extraer_mallas(componentes)

    assert len(mallas) == 3
    assert [malla["id"] for malla in mallas] == ["M1", "M2", "M3"]


def test_sin_terminales_usa_ciclos_fundamentales():
    componentes = [
        Resistencia("R1", 100.0, "1", "2"),
        Resistencia("R2", 100.0, "2", "3"),
        Resistencia("R3", 100.0, "3", "1"),
    ]
    mallas = extraer_mallas(componentes)

    assert len(mallas) == 1
    assert mallas[0]["sentido"] == "indefinido"
    assert mallas[0]["centroide"] is None


def test_arbol_sin_ciclos_devuelve_lista_vacia():
    posiciones = {"A": (0.0, 0.0), "B": (40.0, 0.0), "C": (80.0, 0.0)}
    componentes = [
        _res("R1", "A", "B", posiciones),
        _res("R2", "B", "C", posiciones),
    ]
    assert extraer_mallas(componentes) == []


def test_orden_determinista_aunque_cambie_el_orden_de_los_componentes():
    _, componentes = _circuito_dos_ventanas()
    mallas_a = extraer_mallas(componentes)
    mallas_b = extraer_mallas(list(reversed(componentes)))

    assert [malla["id"] for malla in mallas_a] == [malla["id"] for malla in mallas_b]
    assert [_ids(malla) for malla in mallas_a] == [_ids(malla) for malla in mallas_b]


def test_graph_builder_delega_en_la_extraccion_geometrica():
    _, componentes = _circuito_dos_ventanas()
    builder = GraphBuilder()
    builder.construir_grafo(componentes)

    mallas = builder.extraer_mallas(componentes)

    assert [malla["id"] for malla in mallas] == ["M1", "M2"]
