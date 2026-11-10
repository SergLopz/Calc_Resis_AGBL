"""Extracción de mallas (ventanas) a partir de la geometría del lienzo.

El método principal construye un *embedding* geométrico: ordena los vecinos de
cada nodo por ángulo y recorre las medias aristas para obtener las caras del
dibujo. Las caras interiores son las ventanas que el usuario ve.

Si el dibujo no es planar (aristas que se cruzan sin compartir nodo), si falta
la geometría de algún componente o si una cara es degenerada, se recurre al
método topológico de ciclos fundamentales (árbol de expansión + co-árbol),
manteniendo el orden y la orientación lo más deterministas posible.
"""

from __future__ import annotations

import math
from itertools import pairwise

import networkx as nx

from calc_resis_agbl.models.componentes import CircuitoError

TOLERANCIA_FILA = 10.0
EPS_AREA = 1e-9


def _extremos(componente) -> tuple[str, str]:
    """Devuelve los dos nodos que conecta un componente."""
    if hasattr(componente, "nodo_a"):
        return str(componente.nodo_a), str(componente.nodo_b)
    return str(componente.nodo_positivo), str(componente.nodo_negativo)


def _terminales(componente):
    """Devuelve los dos terminales geométricos de un componente."""
    if hasattr(componente, "terminal_a"):
        return componente.terminal_a, componente.terminal_b
    return componente.terminal_positivo, componente.terminal_negativo


def _posiciones_nodos(componentes) -> dict[str, tuple[float, float]] | None:
    """
    Calcula la posición de cada nodo como el promedio de sus terminales.

    Devuelve ``None`` si algún componente no tiene terminales, porque en ese
    caso no hay geometría fiable para construir el embedding.
    """
    acumulado: dict[str, list[float]] = {}
    for comp in componentes:
        terminal_a, terminal_b = _terminales(comp)
        if terminal_a is None or terminal_b is None:
            return None
        nodo_a, nodo_b = _extremos(comp)
        for nodo, terminal in ((nodo_a, terminal_a), (nodo_b, terminal_b)):
            datos = acumulado.setdefault(nodo, [0.0, 0.0, 0.0])
            datos[0] += float(terminal.x)
            datos[1] += float(terminal.y)
            datos[2] += 1.0
    return {nodo: (datos[0] / datos[2], datos[1] / datos[2]) for nodo, datos in acumulado.items()}


def _grafo_simple(componentes) -> tuple[nx.Graph, dict[frozenset, list[object]]]:
    """
    Construye un grafo simple (sin paralelos ni auto-lazos) y conserva, para
    cada par de nodos, la lista de componentes que lo conectan.

    Los componentes se ordenan por id para que la extracción sea determinista
    aunque el lienzo entregue los items en otro orden.
    """
    grafo = nx.Graph()
    aristas: dict[frozenset, list[object]] = {}
    for comp in sorted(componentes, key=lambda c: str(c.id)):
        nodo_a, nodo_b = _extremos(comp)
        if nodo_a == nodo_b:
            continue
        par = frozenset((nodo_a, nodo_b))
        aristas.setdefault(par, []).append(comp)
        if not grafo.has_edge(nodo_a, nodo_b):
            grafo.add_edge(nodo_a, nodo_b)
    return grafo, aristas


def _rotaciones(grafo: nx.Graph, posiciones: dict[str, tuple[float, float]]) -> dict[str, list[str]]:
    """Ordena los vecinos de cada nodo por ángulo (horario visual en Qt)."""
    rotacion: dict[str, list[str]] = {}
    for nodo in grafo.nodes():
        x0, y0 = posiciones[nodo]
        vecinos = list(grafo.neighbors(nodo))
        vecinos.sort(
            key=lambda vecino: (
                math.atan2(posiciones[vecino][1] - y0, posiciones[vecino][0] - x0),
                str(vecino),
            )
        )
        rotacion[nodo] = vecinos
    return rotacion


def _siguiente(rotacion: dict[str, list[str]], origen: str, destino: str) -> str:
    """
    Siguiente nodo al recorrer una cara.

    Con el orden angular ascendente (horario en pantalla) se toma el vecino
    anterior al de llegada; así las caras interiores quedan en sentido horario.
    """
    vecinos = rotacion[destino]
    indice = vecinos.index(origen)
    return vecinos[(indice - 1) % len(vecinos)]


def _caras(grafo: nx.Graph, rotacion: dict[str, list[str]]) -> list[list[str]]:
    """Recorre todas las medias aristas y devuelve las caras del embedding."""
    visitadas: set[tuple[str, str]] = set()
    caras: list[list[str]] = []
    for nodo_a, nodo_b in grafo.edges():
        for inicio in ((nodo_a, nodo_b), (nodo_b, nodo_a)):
            if inicio in visitadas:
                continue
            cara: list[str] = []
            actual = inicio
            while actual not in visitadas:
                visitadas.add(actual)
                cara.append(actual[0])
                actual = (actual[1], _siguiente(rotacion, actual[0], actual[1]))
            caras.append(cara)
    return caras


def _area_firmada(nodos: list[str], posiciones: dict[str, tuple[float, float]]) -> float:
    """Área con signo del polígono; positiva = horario en coordenadas de Qt."""
    total = 0.0
    for nodo_a, nodo_b in pairwise(list(nodos) + [nodos[0]]):
        xa, ya = posiciones[nodo_a]
        xb, yb = posiciones[nodo_b]
        total += xa * yb - xb * ya
    return total / 2.0


def _centroide(nodos: list[str], posiciones: dict[str, tuple[float, float]]) -> tuple[float, float]:
    """Centroide simple (promedio de vértices) de una cara."""
    xs = [posiciones[nodo][0] for nodo in nodos]
    ys = [posiciones[nodo][1] for nodo in nodos]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _ramas_desde_nodos(
    nodos: list[str], aristas: dict[frozenset, list[object]]
) -> list[dict]:
    """Convierte una secuencia cerrada de nodos en ramas con sentido."""
    ramas = []
    for origen, destino in pairwise(list(nodos) + [nodos[0]]):
        par = frozenset((origen, destino))
        componente = aristas[par][0]
        ramas.append({"origen": origen, "destino": destino, "elemento": componente})
    return ramas


def _malla(
    nodos: list[str],
    posiciones: dict[str, tuple[float, float]],
    aristas: dict[frozenset, list[object]],
) -> dict:
    """Construye una malla horaria a partir de una cara."""
    area = _area_firmada(nodos, posiciones)
    if area < 0:
        nodos = list(reversed(nodos))
        area = -area
    return {
        "sentido": "horario",
        "area": area,
        "centroide": _centroide(nodos, posiciones),
        "nodos": list(nodos),
        "ramas": _ramas_desde_nodos(nodos, aristas),
    }


def _mallas_de_caras(
    caras: list[list[str]],
    posiciones: dict[str, tuple[float, float]],
    aristas: dict[frozenset, list[object]],
) -> list[dict] | None:
    """
    Descarta la cara exterior y convierte las interiores en mallas.

    Devuelve ``None`` si el embedding no permite identificar con seguridad la
    cara exterior o si alguna cara es degenerada (área cero).
    """
    areas = [_area_firmada(cara, posiciones) for cara in caras]
    negativas = [indice for indice, area in enumerate(areas) if area < -EPS_AREA]
    if not negativas:
        return None
    exterior = min(negativas, key=lambda indice: areas[indice])
    mallas = []
    for indice, cara in enumerate(caras):
        if indice == exterior:
            continue
        if abs(areas[indice]) <= EPS_AREA:
            return None
        mallas.append(_malla(cara, posiciones, aristas))
    return mallas


def _orientacion(a, b, c) -> int:
    valor = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if abs(valor) < EPS_AREA:
        return 0
    return 1 if valor > 0 else -1


def _segmentos_se_cruzan(p1, p2, p3, p4) -> bool:
    """Cruza propio entre dos segmentos (sin contar extremos compartidos)."""
    o1 = _orientacion(p1, p2, p3)
    o2 = _orientacion(p1, p2, p4)
    o3 = _orientacion(p3, p4, p1)
    o4 = _orientacion(p3, p4, p2)
    return o1 * o2 < 0 and o3 * o4 < 0


def _hay_cruces(grafo: nx.Graph, posiciones: dict[str, tuple[float, float]]) -> bool:
    """Detecta aristas no adyacentes que se cruzan geométricamente."""
    aristas = list(grafo.edges())
    for indice, (u1, v1) in enumerate(aristas):
        for u2, v2 in aristas[indice + 1 :]:
            if len({u1, v1, u2, v2}) < 4:
                continue
            if _segmentos_se_cruzan(
                posiciones[u1], posiciones[v1], posiciones[u2], posiciones[v2]
            ):
                return True
    return False


def _componentes_con_ciclos(grafo: nx.Graph) -> list[nx.Graph]:
    """
    Devuelve las componentes 2-arista-conexas (sin puentes).

    Un puente no pertenece a ninguna malla; al quitarlo, las ventanas anidadas
    quedan como componentes separadas y se pueden mallar por su cuenta.
    """
    puentes = {frozenset(arista) for arista in nx.bridges(grafo)}
    grafo_ciclos = grafo.copy()
    grafo_ciclos.remove_edges_from([tuple(arista) for arista in puentes])
    componentes = []
    for nodos in nx.connected_components(grafo_ciclos):
        subgrafo = grafo_ciclos.subgraph(nodos).copy()
        if subgrafo.number_of_edges() > 0:
            componentes.append(subgrafo)
    return componentes


def _mallas_fundamentales(
    grafo: nx.Graph, aristas: dict[frozenset, list[object]]
) -> list[dict]:
    """Fallback topológico: un ciclo por cada arista fuera del árbol de expansión."""
    arbol = nx.minimum_spanning_tree(grafo)
    mallas = []
    for nodo_a, nodo_b in grafo.edges():
        if arbol.has_edge(nodo_a, nodo_b):
            continue
        camino = nx.shortest_path(arbol, nodo_a, nodo_b)
        nodos = camino + [nodo_a]
        ramas = []
        for origen, destino in pairwise(nodos):
            par = frozenset((origen, destino))
            ramas.append(
                {
                    "origen": str(origen),
                    "destino": str(destino),
                    "elemento": aristas[par][0],
                }
            )
        mallas.append({"nodos": [str(nodo) for nodo in camino], "ramas": ramas})
    return mallas


def _orientar_mallas(
    mallas: list[dict], posiciones: dict[str, tuple[float, float]] | None
) -> None:
    """Orienta los ciclos del fallback en sentido horario cuando hay geometría."""
    if posiciones is None:
        for malla in mallas:
            malla["sentido"] = "indefinido"
            malla["area"] = None
            malla["centroide"] = None
        return

    for malla in mallas:
        nodos = [str(nodo) for nodo in malla["nodos"]]
        area = _area_firmada(nodos, posiciones)
        if area < 0:
            malla["ramas"] = [
                {
                    "origen": rama["destino"],
                    "destino": rama["origen"],
                    "elemento": rama["elemento"],
                }
                for rama in reversed(malla["ramas"])
            ]
            nodos = list(reversed(nodos))
            area = -area
        malla["sentido"] = "horario"
        malla["area"] = area
        malla["centroide"] = _centroide(nodos, posiciones)
        malla["nodos"] = nodos


def _ordenar_mallas(mallas: list[dict], tolerancia: float) -> list[dict]:
    """
    Numera las mallas de abajo hacia arriba y de izquierda a derecha.

    Las mallas con el mismo centroide (por ejemplo, ventanas anidadas) se
    desempatan por área, dejando primero la más pequeña.
    """
    if not mallas:
        return []

    if any(malla.get("centroide") is None for malla in mallas):
        ordenadas = sorted(
            mallas,
            key=lambda malla: tuple(
                sorted(str(rama["elemento"].id) for rama in malla["ramas"])
            ),
        )
    else:
        pendientes = sorted(
            mallas, key=lambda malla: (-malla["centroide"][1], malla["centroide"][0])
        )
        filas: list[list] = []
        for malla in pendientes:
            y = malla["centroide"][1]
            if filas and abs(y - filas[-1][0]) <= tolerancia:
                filas[-1][1].append(malla)
            else:
                filas.append([y, [malla]])
        ordenadas = []
        for _, fila in filas:
            fila.sort(
                key=lambda malla: (
                    malla["centroide"][0],
                    malla.get("area") if malla.get("area") is not None else 0.0,
                )
            )
            ordenadas.extend(fila)

    for indice, malla in enumerate(ordenadas, start=1):
        malla["id"] = f"M{indice}"
    return ordenadas


def extraer_mallas(componentes, tolerancia_fila: float = TOLERANCIA_FILA) -> list[dict]:
    """
    Extrae las mallas del circuito.

    Cada malla es un diccionario con ``id`` (M1, M2...), ``sentido``,
    ``centroide``, ``area``, ``nodos`` y ``ramas``. Las ramas incluyen
    ``origen``, ``destino`` y ``elemento`` para que el solver construya el
    sistema R·I = V.
    """
    if not componentes:
        raise CircuitoError("El circuito no tiene ramas para analizar.")

    grafo, aristas = _grafo_simple(componentes)
    if grafo.number_of_edges() == 0:
        raise CircuitoError("El circuito no tiene ramas para analizar.")
    if not nx.is_connected(grafo):
        raise CircuitoError(
            "El grafo tiene nodos desconectados; todas las ramas deben estar unidas."
        )

    posiciones = _posiciones_nodos(componentes)
    if posiciones is not None:
        mallas: list[dict] | None = []
        for subgrafo in _componentes_con_ciclos(grafo):
            if _hay_cruces(subgrafo, posiciones):
                mallas = None
                break
            caras = _caras(subgrafo, _rotaciones(subgrafo, posiciones))
            parciales = _mallas_de_caras(caras, posiciones, aristas)
            if parciales is None:
                mallas = None
                break
            mallas.extend(parciales)
        if mallas is not None:
            return _ordenar_mallas(mallas, tolerancia_fila)

    mallas = _mallas_fundamentales(grafo, aristas)
    _orientar_mallas(mallas, posiciones)
    return _ordenar_mallas(mallas, tolerancia_fila)
