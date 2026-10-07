from calc_resis_agbl.core.graph_builder import GraphBuilder
from calc_resis_agbl.models.componentes import Resistencia


def test_clasificacion_nodos_simples_y_esenciales():
    """Valida la clasificación autómata de nodos según su grado topológico."""
    builder = GraphBuilder()

    # 3 resistencias formando un nodo T (Grado 3) y dos extremos (Grado 1 y 2)
    r1 = Resistencia("R1", 100, nodo_a="A", nodo_b="B")
    r2 = Resistencia("R2", 200, nodo_a="B", nodo_b="C")
    r3 = Resistencia("R3", 300, nodo_a="B", nodo_b="D")

    builder.construir_grafo([r1, r2, r3])
    simples, esenciales = builder.clasificar_nodos()

    # El nodo "B" tiene 3 ramas conectadas -> Debe ser esencial
    assert "B" in esenciales
    # Los nodos A, C y D tienen grado < 3 -> No deben ser esenciales
    assert "B" not in simples
