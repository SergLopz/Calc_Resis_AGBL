from dataclasses import dataclass

from calc_resis_agbl.models.componentes import Terminal


@dataclass(frozen=True)
class Punto:
    """Coordenada lógica en la grilla del lienzo (unidades enteras)."""

    x: int
    y: int


def snap_a_grilla(x: float, y: float, tamano: int) -> Punto:
    """Ajusta una coordenada real al nodo de grilla más cercano."""
    return Punto(round(x / tamano), round(y / tamano))


def snap_con_iman(
    x: float,
    y: float,
    tamano: int,
    puntos_existentes: list[Punto],
    radio_iman: int,
) -> Punto:
    """
    Ajusta a grilla y, si hay un punto existente dentro del radio de imán
    (en celdas de grilla), devuelve ese punto para fusionar la conexión.
    """
    candidato = snap_a_grilla(x, y, tamano)
    mejor = candidato
    mejor_dist = radio_iman + 1
    for p in puntos_existentes:
        dist = max(abs(p.x - candidato.x), abs(p.y - candidato.y))
        if dist <= radio_iman and dist < mejor_dist:
            mejor = p
            mejor_dist = dist
    return mejor


class DetectorNodos:
    """
    Agrupa terminales que comparten la misma posición en la grilla en un único
    nodo eléctrico. Terminales con coordenadas distintas = nodos distintos.
    """

    def __init__(self, tamano_grilla: int = 20, radio_iman: int = 1):
        self.tamano_grilla = tamano_grilla
        self.radio_iman = radio_iman

    def agrupar(
        self, terminales: dict[str, Terminal]
    ) -> dict[str, list[str]]:
        """
        Recibe un mapa id_terminal -> Terminal y devuelve
        id_nodo -> lista de ids de terminales que lo componen.

        El id_nodo es una etiqueta estable derivada de la celda de grilla,
        p. ej. 'N(3,4)', independiente del orden de inserción.
        """
        grupos: dict[str, list[str]] = {}
        for id_terminal, term in terminales.items():
            punto = snap_a_grilla(term.x, term.y, self.tamano_grilla)
            id_nodo = f"N({punto.x},{punto.y})"
            grupos.setdefault(id_nodo, []).append(id_terminal)
        return grupos

    def nodos_de_componentes(
        self, componentes: list[object]
    ) -> dict[str, tuple[str, str]]:
        """
        Para cada componente devuelve (id_componente, tipo, nodo_a, nodo_b),
        resolviendo sus terminales a ids de nodo. Si un componente no tiene
        terminales asignados, usa un nodo propio derivado de su id.
        """
        terminales: dict[str, Terminal] = {}
        mapa_comp: dict[str, tuple[str, str, str, str]] = {}

        for comp in componentes:
            tipo = getattr(comp, "tipo", None)
            if tipo == "R":
                pa = getattr(comp, "terminal_a", None)
                pb = getattr(comp, "terminal_b", None)
            else:
                pa = getattr(comp, "terminal_positivo", None)
                pb = getattr(comp, "terminal_negativo", None)
            if pa is not None:
                terminales[f"{comp.id}:a"] = pa
            if pb is not None:
                terminales[f"{comp.id}:b"] = pb
            mapa_comp[comp.id] = (tipo, f"{comp.id}:a", f"{comp.id}:b")

        grupos = self.agrupar(terminales)
        nodo_de_terminal: dict[str, str] = {}
        for id_nodo, terminales_del_nodo in grupos.items():
            for id_terminal in terminales_del_nodo:
                nodo_de_terminal[id_terminal] = id_nodo

        resuelto: dict[str, tuple[str, str, str]] = {}
        for comp_id, (tipo, ta, tb) in mapa_comp.items():
            na = nodo_de_terminal.get(ta, f"{comp_id}:NA")
            nb = nodo_de_terminal.get(tb, f"{comp_id}:NB")
            resuelto[comp_id] = (tipo, na, nb)
        return resuelto
