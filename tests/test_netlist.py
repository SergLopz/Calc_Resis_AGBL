from calc_resis_agbl.core.netlist import (
    DetectorNodos,
    Punto,
    snap_a_grilla,
    snap_con_iman,
)
from calc_resis_agbl.models.componentes import Resistencia, Terminal


def test_snap_a_grilla_redondea_al_nodo_mas_cercano():
    assert snap_a_grilla(18, 2, 20) == Punto(1, 0)
    assert snap_a_grilla(-9, -31, 20) == Punto(0, -2)


def test_snap_con_iman_atrae_a_punto_existente():
    existentes = [Punto(2, 2)]
    # (39, 41) -> celda (2,2), dentro del radio de imán -> devuelve el existente.
    assert snap_con_iman(39, 41, 20, existentes, radio_iman=1) == Punto(2, 2)
    # Un punto lejano no se imanta.
    assert snap_con_iman(200, 200, 20, existentes, radio_iman=1) == Punto(10, 10)


def test_terminales_en_misma_celda_forman_un_nodo():
    detector = DetectorNodos(tamano_grilla=20)
    r1 = Resistencia("R1", 100, "?", "?", terminal_a=Terminal(0, 0), terminal_b=Terminal(20, 0))
    r2 = Resistencia("R2", 100, "?", "?", terminal_a=Terminal(0, 0), terminal_b=Terminal(0, 20))

    grupos = detector.agrupar(
        {"r1a": r1.terminal_a, "r1b": r1.terminal_b, "r2a": r2.terminal_a, "r2b": r2.terminal_b}
    )
    # r1a y r2a comparten celda (0,0) -> mismo nodo
    nodo_compartido = [k for k, v in grupos.items() if len(v) == 2]
    assert len(nodo_compartido) == 1


def test_nodos_de_componentes_resuelve_uniones():
    detector = DetectorNodos(tamano_grilla=20)
    r1 = Resistencia("R1", 100, "?", "?", terminal_a=Terminal(0, 0), terminal_b=Terminal(20, 0))
    r2 = Resistencia("R2", 100, "?", "?", terminal_a=Terminal(20, 0), terminal_b=Terminal(40, 0))
    resuelto = detector.nodos_de_componentes([r1, r2])
    _, r1_a, r1_b = resuelto["R1"]
    _, r2_a, _r2_b = resuelto["R2"]
    # El terminal compartido (20,0) debe ser el mismo nodo en ambos.
    assert r1_b == r2_a
    assert r1_a != r1_b
