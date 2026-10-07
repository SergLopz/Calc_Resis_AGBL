from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsItem


class ResistenciaItem(QGraphicsItem):
    """Representación gráfica interactiva (vectorial) de una resistencia en el lienzo."""

    def __init__(self, id_comp: str, valor: float, x: float = 0, y: float = 0):
        super().__init__()
        self.id_comp = id_comp
        self.valor = valor
        self.setPos(x, y)

        # Permitir movimiento y selección en el lienzo
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

    def boundingRect(self) -> QRectF:
        """Define el área delimitadora para la detección de clics y redibujado."""
        return QRectF(-10, -20, 100, 40)

    def paint(self, painter: QPainter, option, widget=None):
        """Dibuja el símbolo zig-zag estándar de la resistencia."""
        pen = QPen(QColor("#00FFCC") if self.isSelected() else QColor("#FFFFFF"), 2)
        painter.setPen(pen)

        # Dibujar terminales y zigzag
        painter.drawLine(-10, 0, 10, 0)
        painter.drawLine(10, 0, 20, -10)
        painter.drawLine(20, -10, 30, 10)
        painter.drawLine(30, 10, 40, -10)
        painter.drawLine(40, -10, 50, 10)
        painter.drawLine(50, 10, 60, 0)
        painter.drawLine(60, 0, 80, 0)

        # Dibujar texto informativo (Etiqueta y valor)
        painter.setPen(QColor("#CCCCCC"))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(15, -15, f"{self.id_comp} ({self.valor}Ω)")
