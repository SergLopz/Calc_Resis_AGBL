from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsObject,
    QGraphicsPathItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

COLOR_BORDE = QColor("#FFFFFF")
COLOR_SELECCION = QColor("#00FFCC")
COLOR_TEXTO = QColor("#CCCCCC")
COLOR_CABLE = QColor("#DDDDDD")

LARGO_TERMINAL = 20.0
TAMANO_GRILLA = 20


class BaseComponente(QGraphicsObject):
    """
    Elemento gráfico base para componentes de dos terminales.

    Los terminales son puntos fijos (locales) que sirven de imán para las
    conexiones. Al moverse el componente, los terminales se recalculan en
    coordenadas de escena vía `terminales_escena()`.
    """

    def __init__(self, id_comp: str, valor: float):
        super().__init__()
        self.id_comp = id_comp
        self.valor = valor
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)

    def itemChange(self, change, value):
        """Ajusta la posición a la grilla al arrastrar (snap)."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            return QPointF(
                round(value.x() / TAMANO_GRILLA) * TAMANO_GRILLA,
                round(value.y() / TAMANO_GRILLA) * TAMANO_GRILLA,
            )
        return super().itemChange(change, value)

    # --- Geometría de terminales (implementan las subclases) ---
    def terminal_local_a(self) -> QPointF:  # pragma: no cover - interfaz
        raise NotImplementedError

    def terminal_local_b(self) -> QPointF:  # pragma: no cover - interfaz
        raise NotImplementedError

    def terminales_escena(self) -> tuple[QPointF, QPointF]:
        return (
            self.mapToScene(self.terminal_local_a()),
            self.mapToScene(self.terminal_local_b()),
        )

    def boundingRect(self) -> QRectF:  # pragma: no cover - interfaz
        raise NotImplementedError

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:  # pragma: no cover - interfaz
        raise NotImplementedError

    def _pen(self) -> QPen:
        color = COLOR_SELECCION if self.isSelected() else COLOR_BORDE
        return QPen(color, 2)


class ResistenciaItem(BaseComponente):
    """Símbolo zig-zag estándar de una resistencia con dos terminales simétricos."""

    # Terminales en ±40 (múltiplo de la grilla) para que al rotar 90° sigan
    # cayendo en celdas de grilla. Cuerpo útil entre -20 y +20.
    MEDIO = 40.0
    CUERPO = 40.0

    def __init__(self, id_comp: str, valor: float, x: float = 0, y: float = 0):
        super().__init__(id_comp, valor)
        self.setPos(x, y)

    def terminal_local_a(self) -> QPointF:
        return QPointF(-self.MEDIO, 0)

    def terminal_local_b(self) -> QPointF:
        return QPointF(self.MEDIO, 0)

    def boundingRect(self) -> QRectF:
        return QRectF(-self.MEDIO - 4, -24, 2 * self.MEDIO + 8, 48)

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen())
        medio_cuerpo = self.CUERPO / 2
        painter.drawLine(QPointF(-self.MEDIO, 0), QPointF(-medio_cuerpo, 0))
        paso = self.CUERPO / 6.0
        pts = [QPointF(-medio_cuerpo + i * paso,
                       -10 if i % 2 else 10) for i in range(7)]
        pts[0] = QPointF(-medio_cuerpo, 0)
        pts[-1] = QPointF(medio_cuerpo, 0)
        for i in range(len(pts) - 1):
            painter.drawLine(pts[i], pts[i + 1])
        painter.drawLine(QPointF(medio_cuerpo, 0), QPointF(self.MEDIO, 0))
        self._dibujar_puntos_terminal(painter)
        painter.setPen(COLOR_TEXTO)
        painter.setFont(QFont("Arial", 8))
        painter.drawText(QRectF(-self.MEDIO, -40, 2 * self.MEDIO, 14),
                         Qt.AlignmentFlag.AlignCenter,
                         f"{self.id_comp} ({self.valor:g}Ω)")

    def _dibujar_puntos_terminal(self, painter: QPainter) -> None:
        painter.setBrush(COLOR_TEXTO)
        r = 3.0
        painter.drawEllipse(self.terminal_local_a(), r, r)
        painter.drawEllipse(self.terminal_local_b(), r, r)
        painter.setBrush(Qt.BrushStyle.NoBrush)


class FuenteItem(BaseComponente):
    """Símbolo de fuente de voltaje DC con polaridad y terminales simétricos."""

    MEDIO = 40.0
    RADIO = 16.0

    def __init__(self, id_comp: str, valor: float, x: float = 0, y: float = 0):
        super().__init__(id_comp, valor)
        self.setPos(x, y)

    def terminal_local_a(self) -> QPointF:
        return QPointF(-self.MEDIO, 0)

    def terminal_local_b(self) -> QPointF:
        return QPointF(self.MEDIO, 0)

    def boundingRect(self) -> QRectF:
        return QRectF(
            -self.MEDIO - 4,
            -self.RADIO - 24,
            2 * self.MEDIO + 8,
            self.RADIO * 2 + 48,
        )

    def paint(self, painter, option, widget=None):
        painter.setPen(self._pen())
        painter.drawLine(QPointF(-self.MEDIO, 0), QPointF(-self.RADIO, 0))
        painter.drawEllipse(QPointF(0, 0), self.RADIO, self.RADIO)
        painter.drawLine(QPointF(self.RADIO, 0), QPointF(self.MEDIO, 0))
        painter.drawLine(QPointF(-6, -self.RADIO + 5), QPointF(-6, self.RADIO - 5))
        painter.drawLine(QPointF(6, -self.RADIO + 5), QPointF(6, self.RADIO - 5))
        painter.setBrush(COLOR_TEXTO)
        r = 3.0
        painter.drawEllipse(self.terminal_local_a(), r, r)
        painter.drawEllipse(self.terminal_local_b(), r, r)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(COLOR_TEXTO)
        painter.setFont(QFont("Arial", 8))
        painter.drawText(QRectF(-self.MEDIO, -self.RADIO - 24, 2 * self.MEDIO, 14),
                         Qt.AlignmentFlag.AlignCenter,
                         f"{self.id_comp} ({self.valor:g}V)")


class CableItem(QGraphicsPathItem):
    """Cable visual que une dos terminales de componentes."""

    def __init__(self, origen: QPointF, destino: QPointF):
        super().__init__()
        pen = QPen(COLOR_CABLE, 2)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setZValue(-1)
        self.actualizar(origen, destino)

    def actualizar(self, origen: QPointF, destino: QPointF) -> None:
        from PyQt6.QtGui import QPainterPath

        path = QPainterPath(origen)
        path.lineTo(destino)
        self.setPath(path)


class TierraItem(QGraphicsItem):
    """Símbolo de tierra: marca visualmente el nodo de referencia (0 V)."""

    Z = 5

    def __init__(self, x: float, y: float):
        super().__init__()
        self.setPos(x, y)
        self.setZValue(self.Z)

    def boundingRect(self) -> QRectF:
        return QRectF(-16, -2, 32, 22)

    def paint(self, painter, option, widget=None):
        pen = QPen(QColor("#FBBF24"), 2)
        painter.setPen(pen)
        painter.drawLine(QPointF(0, 0), QPointF(0, 10))
        painter.drawLine(QPointF(-14, 10), QPointF(14, 10))
        painter.drawLine(QPointF(-9, 15), QPointF(9, 15))
        painter.drawLine(QPointF(-4, 20), QPointF(4, 20))
