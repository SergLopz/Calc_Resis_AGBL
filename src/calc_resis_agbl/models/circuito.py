from calc_resis_agbl.models.componentes import (
    MAX_FUENTES,
    MAX_RESISTENCIAS,
    NODO_REFERENCIA,
    CircuitoError,
    FuenteDC,
    Resistencia,
)


class Circuito:
    """Modelo contenedor del estado completo del circuito eléctrico."""

    def __init__(self):
        self.resistencias: list[Resistencia] = []
        self.fuentes: list[FuenteDC] = []

    def agregar_resistencia(self, resistencia: Resistencia) -> None:
        """Añade una nueva resistencia al modelo validando el tope del grupo."""
        if len(self.resistencias) >= MAX_RESISTENCIAS:
            raise CircuitoError(
                f"Se alcanzó el límite de {MAX_RESISTENCIAS} resistencias."
            )
        self._validar_nombre_unico(resistencia.id)
        if resistencia.valor_ohms <= 0:
            raise CircuitoError(f"{resistencia.id}: la resistencia debe ser mayor que 0 Ω.")
        self.resistencias.append(resistencia)

    def agregar_fuente(self, fuente: FuenteDC) -> None:
        """Añade una nueva fuente de voltaje al modelo validando el tope del grupo."""
        if len(self.fuentes) >= MAX_FUENTES:
            raise CircuitoError(f"Se alcanzó el límite de {MAX_FUENTES} fuentes DC.")
        self._validar_nombre_unico(fuente.id)
        self.fuentes.append(fuente)

    def _validar_nombre_unico(self, id_comp: str) -> None:
        existentes = {c.id for c in self.obtener_todos_los_componentes()}
        if not id_comp or id_comp in existentes:
            raise CircuitoError(
                f"El identificador '{id_comp}' está vacío o ya existe en el circuito."
            )

    def obtener_todos_los_componentes(self) -> list[object]:
        """Devuelve una lista unificada de todos los elementos del circuito."""
        return self.resistencias + self.fuentes

    def nodos_usados(self) -> set[str]:
        """Conjunto de identificadores de nodo referenciados por los componentes."""
        nodos: set[str] = set()
        for r in self.resistencias:
            nodos.update((r.nodo_a, r.nodo_b))
        for f in self.fuentes:
            nodos.update((f.nodo_positivo, f.nodo_negativo))
        return nodos

    def validar(self) -> None:
        """Validaciones topológicas previas a la resolución."""
        if not self.obtener_todos_los_componentes():
            raise CircuitoError("Agrega al menos un componente al circuito.")
        nodos = self.nodos_usados()
        if len(nodos) < 2:
            raise CircuitoError("El circuito necesita al menos dos nodos distintos.")
        if NODO_REFERENCIA not in nodos:
            raise CircuitoError(
                f"Incluye el nodo de referencia '{NODO_REFERENCIA}' (tierra) en alguna rama."
            )

    def limpiar(self) -> None:
        """Reinicia el circuito eliminando todos los componentes."""
        self.resistencias.clear()
        self.fuentes.clear()
