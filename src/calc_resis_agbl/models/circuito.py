from calc_resis_agbl.models.componentes import FuenteDC, Resistencia


class Circuito:
    """Modelo contenedor del estado completo del circuito eléctrico."""

    def __init__(self):
        self.resistencias: list[Resistencia] = []
        self.fuentes: list[FuenteDC] = []

    def agregar_resistencia(self, resistencia: Resistencia) -> None:
        """Añade una nueva resistencia al modelo."""
        self.resistencias.append(resistencia)

    def agregar_fuente(self, fuente: FuenteDC) -> None:
        """Añade una nueva fuente de voltaje al modelo."""
        self.fuentes.append(fuente)

    def obtener_todos_los_componentes(self) -> list[object]:
        """Devuelve una lista unificada de todos los elementos del circuito."""
        return self.resistencias + self.fuentes

    def limpiar(self) -> None:
        """Reinicia el circuito eliminando todos los componentes."""
        self.resistencias.clear()
        self.fuentes.clear()
