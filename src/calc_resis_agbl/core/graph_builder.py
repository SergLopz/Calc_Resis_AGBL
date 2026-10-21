from itertools import pairwise

import networkx as nx

from calc_resis_agbl.models.componentes import CircuitoError, Nodo, Resistencia


class GraphBuilder:
    """
    Convierte la lista de componentes y terminales en un grafo topológico y
    extrae la base de ciclos fundamentales (mallas) mediante un spanning tree.
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

    def fuente_mayor(self, componentes: list[object]) -> object | None:
        """Fuente DC de mayor magnitud; sirve de pivote para orientar la malla 1."""
        fuentes = [c for c in componentes if hasattr(c, "valor_voltios")]
        if not fuentes:
            return None
        return max(fuentes, key=lambda f: abs(f.valor_voltios))

    def extraer_mallas(self, componentes: list[object]) -> list[dict]:
        """
        Extrae la base de ciclos fundamentales del grafo.

        Para cada arista fuera del spanning tree se reconstruye el lazo que
        forma con el camino único del árbol. Cada malla resultante se devuelve
        como una lista ordenada de (nodo_origen, nodo_destino, key, elemento)
        recorriendo el lazo en un sentido consistente.

        La primera malla se orienta según la fuente de mayor magnitud: si esa
        fuente participa en la malla, se invierte el recorrido para que su
        corriente salga del polo positivo hacia el negativo.
        """
        if self.graph.number_of_edges() == 0:
            raise CircuitoError("El circuito no tiene ramas para analizar.")

        # MultiGraph -> grafo simple para el árbol de expansión (paralelos actúan igual).
        simple = nx.Graph()
        for u, v, _key, data in self.graph.edges(keys=True, data=True):
            if not simple.has_edge(u, v):
                simple.add_edge(u, v, elemento=data["elemento"])
            elif "paralelos" not in simple[u][v]:
                simple[u][v]["paralelos"] = True

        if not nx.is_connected(simple):
            raise CircuitoError(
                "El grafo tiene nodos desconectados; todas las ramas deben estar unidas."
            )

        arbol = nx.minimum_spanning_tree(simple)
        co_tree = [e for e in simple.edges() if not arbol.has_edge(*e)]

        mallas: list[dict] = []
        for u, v in co_tree:
            camino = nx.shortest_path(arbol, u, v)
            # Lazo: camino del árbol u->v más la arista co-tree v->u (cierra el ciclo).
            lazo_nodos = camino + [u]
            mallas.append(self._lazo_a_ramas(lazo_nodos, componentes))

        self._orientar_primera_malla(mallas, componentes)
        return mallas

    def _lazo_a_ramas(self, lazo_nodos: list[str], componentes: list[object]) -> dict:
        """Convierte una secuencia de nodos del lazo en ramas con sentido de recorrido."""
        por_par: dict[frozenset, list[object]] = {}
        for c in componentes:
            if isinstance(c, Resistencia):
                par = frozenset((c.nodo_a, c.nodo_b))
            elif hasattr(c, "nodo_positivo"):
                par = frozenset((c.nodo_positivo, c.nodo_negativo))
            else:
                continue
            por_par.setdefault(par, []).append(c)

        ramas = []
        for origen, destino in pairwise(lazo_nodos):
            para_este_par = por_par.get(frozenset((origen, destino)), [])
            if not para_este_par:
                raise CircuitoError(
                    f"No se encontró rama física entre nodos {origen} y {destino}."
                )
            for elemento in para_este_par:
                ramas.append(
                    {"origen": str(origen), "destino": str(destino), "elemento": elemento}
                )
        return {"ramas": ramas}

    def _orientar_primera_malla(self, mallas: list[dict], componentes: list[object]) -> None:
        """Orienta la malla 1 según la fuente de mayor magnitud (polo + -> polo -)."""
        if not mallas:
            return
        fuente = self.fuente_mayor(componentes)
        if fuente is None:
            return
        for rama in mallas[0]["ramas"]:
            if rama["elemento"] is fuente:
                coincide = (
                    rama["origen"] == fuente.nodo_positivo
                    and rama["destino"] == fuente.nodo_negativo
                )
                if not coincide:
                    mallas[0]["ramas"].reverse()
                    for rama in mallas[0]["ramas"]:
                        rama["origen"], rama["destino"] = rama["destino"], rama["origen"]
                return
