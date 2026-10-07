from dataclasses import dataclass


@dataclass
class Resistencia:
    """Representa un elemento resistivo dentro del circuito."""

    id: str
    valor_ohms: float
    nodo_a: str
    nodo_b: str
    corriente: float = 0.0  # Calculado post-simulación
    voltaje: float = 0.0  # Calculado post-simulación
    potencia: float = 0.0  # Calculado post-simulación


@dataclass
class FuenteDC:
    """Representa una fuente de voltaje directo."""

    id: str
    valor_voltios: float
    nodo_positivo: str
    nodo_negativo: str
