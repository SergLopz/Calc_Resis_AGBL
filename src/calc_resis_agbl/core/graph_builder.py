import networkx as nx


class GraphBuilder:
    """Convierte la lista de componentes y terminales en un grafo topológico."""

    def __init__(self):
        self.graph = nx.MultiGraph()

    def construir_grafo(self, componentes: list[object]) -> nx.MultiGraph:
        """Agrega nodos y ramas al grafo a partir de los componentes."""
        self.graph.clear()
        for comp in componentes:
            if hasattr(comp, "nodo_a"):
                self.graph.add_edge(
                    comp.nodo_a, comp.nodo_b, key=comp.id, elemento=comp
                )
            elif hasattr(comp, "nodo_positivo"):
                self.graph.add_edge(
                    comp.nodo_positivo, comp.nodo_negativo, key=comp.id, elemento=comp
                )
        return self.graph

    def clasificar_nodos(self) -> tuple[list[str], list[str]]:
        """
        Clasifica nodos en:
        - Simples (Grado == 2) -> Etiquetados en minúsculas (a, b, c)
        - Esenciales (Grado >= 3) -> Etiquetados en mayúsculas (A, B, C)
        """
        simples = []
        esenciales = []
        for nodo, grado in self.graph.degree():
            if grado == 2:
                simples.append(str(nodo))
            elif grado >= 3:
                esenciales.append(str(nodo))
        return simples, esenciales
