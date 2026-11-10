import networkx as nx

from calc_resis_agbl.core.planar_meshes import (
    extraer_mallas as extraer_mallas_geometricas,
)
from calc_resis_agbl.models.componentes import Nodo, Resistencia


class GraphBuilder:
    """
    Convierte la lista de componentes y terminales en un grafo topológico y
    extrae las mallas (ventanas) a partir de la geometría del lienzo.
    """

    def __init__(self):
        self.graph = nx.MultiGraph()

    def construir_grafo(self, componentes: list[object]) -> nx.MultiGraph:
        """Agrega nodos y ramas al grafo a partir de los componentes.

        Cada arista guarda la referencia al componente en el atributo 'elemento'
        y la clave de arista es el id del componente (permite paralelos).
        """
        self.graph.clear()
        for comp in componentes:
            if isinstance(comp, Resistencia):
                self.graph.add_edge(
                    comp.nodo_a, comp.nodo_b, key=comp.id, elemento=comp
                )
            elif hasattr(comp, "nodo_positivo"):
                self.graph.add_edge(
                    comp.nodo_positivo,
                    comp.nodo_negativo,
                    key=comp.id,
                    elemento=comp,
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

    def construir_nodos(self) -> dict[str, Nodo]:
        """Devuelve un diccionario id -> Nodo con grado y etiqueta autoasignada."""
        simples, esenciales = self.clasificar_nodos()
        nodos: dict[str, Nodo] = {}

        def etiquetar(indice: int, mayuscula: bool) -> str:
            letra = chr(ord("A") + indice) if mayuscula else chr(ord("a") + indice)
            return letra

        for i, nid in enumerate(sorted(esenciales)):
            nodos[str(nid)] = Nodo(id=str(nid), etiqueta=etiquetar(i, True))
        for i, nid in enumerate(sorted(simples)):
            nodos[str(nid)] = Nodo(id=str(nid), etiqueta=etiquetar(i, False))
        for nid, grado in self.graph.degree():
            nid = str(nid)
            if nid not in nodos:
                nodos[nid] = Nodo(id=nid, etiqueta=nid)
            nodos[nid].grado = grado
        return nodos

    def extraer_mallas(self, componentes: list[object]) -> list[dict]:
        """Extrae las mallas (ventanas) usando la geometría de los componentes."""
        return extraer_mallas_geometricas(componentes)
