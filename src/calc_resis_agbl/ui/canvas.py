from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView


class CircuitCanvas(QGraphicsView):
    """Lienzo gráfico vectorial para la construcción visual del circuito."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Configuración para renderizado fluido de elementos vectoriales
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QColor("#1E1E1E"))  # Fondo oscuro para alto contraste
        self.scene.setSceneRect(-500, -500, 1000, 1000)

    def keyPressEvent(self, event):
        """Maneja atajos de teclado para accesibilidad (Ej. Insertar R o V)."""
        if event.key() == Qt.Key.Key_R:
            print("Atajo 'R' detectado: Agregar Resistencia al lienzo")
        elif event.key() == Qt.Key.Key_V:
            print("Atajo 'V' detectado: Agregar Fuente de Voltaje al lienzo")
        else:
            super().keyPressEvent(event)
