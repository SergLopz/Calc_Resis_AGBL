from dataclasses import dataclass, field

MAX_RESISTENCIAS = 20
MAX_FUENTES = 3
NODO_REFERENCIA = "0"


class CircuitoError(Exception):
    """Error de validación del circuito (componentes o topología)."""


@dataclass
class Terminal:
    """Punto de conexión físico (coordenadas de lienzo) de un componente."""

    x: float
    y: float


@dataclass
class Resistencia:
    """Representa un elemento resistivo dentro del circuito."""

    id: str
    valor_ohms: float
    nodo_a: str
    nodo_b: str
    terminal_a: Terminal | None = None
    terminal_b: Terminal | None = None
    corriente: float = 0.0  # Calculado post-simulación (de nodo_a hacia nodo_b)
    voltaje: float = 0.0  # Calculado post-simulación (V_a - V_b)
    potencia: float = 0.0  # Calculado post-simulación (disipada)

    @property
    def tipo(self) -> str:
        return "R"


@dataclass
class FuenteDC:
    """Representa una fuente de voltaje directo."""

    id: str
    valor_voltios: float
    nodo_positivo: str
    nodo_negativo: str
    terminal_positivo: Terminal | None = None
    terminal_negativo: Terminal | None = None
    corriente: float = 0.0  # Calculado post-simulación (de + hacia -)
    voltaje: float = 0.0  # Calculado post-simulación (V_+ - V_-)
    potencia: float = 0.0  # Calculado post-simulación (entregada)

    @property
    def tipo(self) -> str:
        return "V"


@dataclass
class Nodo:
    """Punto de unión eléctrica detectado topológicamente."""

    id: str
    grado: int = 0
    coordenada: Terminal | None = None
    etiqueta: str = ""  # minúscula si es simple (grado 2), mayúscula si esencial (grado >= 3)
    es_referencia: bool = False
    terminales_conectados: list[Terminal] = field(default_factory=list)

    @property
    def clasificacion(self) -> str:
        if self.es_referencia:
            return "referencia"
        if self.grado >= 3:
            return "esencial"
        if self.grado == 2:
            return "simple"
        return "extremo"
