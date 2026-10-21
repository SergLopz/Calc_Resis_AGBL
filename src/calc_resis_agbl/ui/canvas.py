from PyQt6.QtCore import QLineF, QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView

from calc_resis_agbl.core.netlist import DetectorNodos, Punto, snap_a_grilla
from calc_resis_agbl.models.componentes import NODO_REFERENCIA
from calc_resis_agbl.ui.graphics_items import (
    BaseComponente,
    CableItem,
    FuenteItem,
    ResistenciaItem,
    TerminalResaltadoItem,
    TierraItem,
)

TAMANO_GRILLA = 20
RADIO_IMAN = 1  # en celdas de grilla


class CircuitCanvas(QGraphicsView):
    """
    Lienzo gráfico vectorial para la construcción visual del circuito.

    - Los componentes se arrastran con el mouse y se ajustan (snap) a la grilla.
    - El terminal de un componente actúa de imán: al soltar cerca de otro
      terminal, se fusionan en el mismo nodo eléctrico.
    - Emite señales para que la ventana principal sincronice el modelo.
    """

    circuito_cambiado = pyqtSignal()
    componente_seleccionado = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QColor("#1E1E1E"))
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)

        self.detector = DetectorNodos(TAMANO_GRILLA, RADIO_IMAN)
        self._contador = {"R": 0, "V": 0}
        self._cables: list[CableItem] = []
        # Conexiones explícitas por cable: cada entrada es
        # ((itemA, idxA), (itemB, idxB)). Se guardan referencias a los items,
        # no coordenadas, para recalcular al mover/rotar/borrar.
        self._conexiones: list[tuple[tuple[BaseComponente, int], tuple[BaseComponente, int]]] = []
        self._modo_conexion = False
        self._terminal_pendiente: tuple[BaseComponente, int] | None = None
        self._resaltado: TerminalResaltadoItem | None = None
        self._nodo_tierra: Punto | None = None
        self._tierra_item: TierraItem | None = None

        self.setMouseTracking(True)
        self.scene.selectionChanged.connect(self._on_selection_changed)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def agregar_resistencia(self, valor: float = 1000.0, pos: QPointF | None = None) -> ResistenciaItem:
        self._contador["R"] += 1
        item = ResistenciaItem(f"R{self._contador['R']}", valor)
        self._colocar(item, pos)
        return item

    def agregar_fuente(self, valor: float = 12.0, pos: QPointF | None = None) -> FuenteItem:
        self._contador["V"] += 1
        item = FuenteItem(f"V{self._contador['V']}", valor)
        self._colocar(item, pos)
        return item

    def componentes(self) -> list[BaseComponente]:
        return [it for it in self.scene.items() if isinstance(it, BaseComponente)]

    def construir_componentes_modelo(self) -> list[object]:
        """
        Traduce los items gráficos a componentes del modelo, resolviendo sus
        terminales a ids de nodo mediante el detector de nodos. Los terminales
        que comparten celda de grilla quedan como el mismo nodo eléctrico.
        """
        from calc_resis_agbl.models.componentes import FuenteDC, Resistencia, Terminal

        bruto: list[object] = []
        for item in self.componentes():
            ta, tb = item.terminales_escena()
            term_a = Terminal(ta.x(), ta.y())
            term_b = Terminal(tb.x(), tb.y())
            if isinstance(item, FuenteItem):
                bruto.append(
                    FuenteDC(
                        item.id_comp,
                        float(item.valor),
                        "?",
                        "?",
                        terminal_positivo=term_a,
                        terminal_negativo=term_b,
                    )
                )
            else:
                bruto.append(
                    Resistencia(
                        item.id_comp,
                        float(item.valor),
                        "?",
                        "?",
                        terminal_a=term_a,
                        terminal_b=term_b,
                    )
                )

        mapa = self.detector.nodos_de_componentes(bruto, self._conexiones_como_ids())
        id_tierra = self._id_nodo_de_celda_tierra(mapa)
        for comp in bruto:
            tipo, na, nb = mapa[comp.id]
            if id_tierra is not None:
                if na == id_tierra:
                    na = NODO_REFERENCIA
                if nb == id_tierra:
                    nb = NODO_REFERENCIA
            if tipo == "R":
                comp.nodo_a, comp.nodo_b = na, nb
            else:
                comp.nodo_positivo, comp.nodo_negativo = na, nb
        return bruto

    def _id_nodo_de_celda_tierra(
        self, mapa: dict[str, tuple[str, str, str]]
    ) -> str | None:
        """
        Determina el id de nodo (según el detector) que corresponde a la celda
        marcada como tierra. Se busca un terminal real en esa celda y se lee el
        nodo resuelto, porque la etiqueta del grupo puede venir de otro terminal
        conectado por cable.
        """
        if self._nodo_tierra is None:
            return None
        celda = self._nodo_tierra
        for item in self.componentes():
            for idx in (0, 1):
                tp = item.terminales_escena()[idx]
                punto = snap_a_grilla(tp.x(), tp.y(), TAMANO_GRILLA)
                if punto.x == celda.x and punto.y == celda.y:
                    _tipo, na, nb = mapa[item.id_comp]
                    return na if idx == 0 else nb
        # Sin componente en la celda: usa la etiqueta cruda por si coincide.
        return self.id_nodo_tierra()

    def id_nodo_tierra(self) -> str | None:
        """Id de nodo correspondiente a la celda marcada como tierra, si existe."""
        if self._nodo_tierra is None:
            return None
        return f"N({self._nodo_tierra.x},{self._nodo_tierra.y})"

    def marcar_tierra_en(self, punto_escena: QPointF) -> bool:
        """Marca la celda de grilla más cercana al punto como nodo de referencia 0."""
        celda = snap_a_grilla(punto_escena.x(), punto_escena.y(), TAMANO_GRILLA)
        self._nodo_tierra = celda
        self._redibujar_tierra()
        self.circuito_cambiado.emit()
        return True

    def limpiar_tierra(self) -> None:
        self._nodo_tierra = None
        self._redibujar_tierra()
        self.circuito_cambiado.emit()

    def _redibujar_tierra(self) -> None:
        if self._tierra_item is not None:
            self.scene.removeItem(self._tierra_item)
            self._tierra_item = None
        if self._nodo_tierra is None:
            return
        self._tierra_item = TierraItem(
            self._nodo_tierra.x * TAMANO_GRILLA,
            self._nodo_tierra.y * TAMANO_GRILLA,
        )
        self.scene.addItem(self._tierra_item)

    def detectar_nodos(self) -> dict:
        """
        Construye el grafo topológico y devuelve los nodos detectados con su
        grado y etiqueta automática (minúsculas si simple, mayúsculas si esencial).
        """
        from calc_resis_agbl.core.graph_builder import GraphBuilder

        comps = self.construir_componentes_modelo()
        builder = GraphBuilder()
        builder.construir_grafo(comps)
        return builder.construir_nodos()

    def limpiar(self) -> None:
        for cable in self._cables:
            self.scene.removeItem(cable)
        self._cables.clear()
        self._conexiones.clear()
        for item in self.componentes():
            self.scene.removeItem(item)
        self._contador = {"R": 0, "V": 0}
        self._terminal_pendiente = None
        self._actualizar_resaltado()
        self._nodo_tierra = None
        self._redibujar_tierra()
        self.circuito_cambiado.emit()

    def activar_modo_conexion(self, activo: bool) -> None:
        self._modo_conexion = activo
        self._terminal_pendiente = None
        self._actualizar_resaltado()
        self.viewport().setCursor(
            Qt.CursorShape.CrossCursor if activo else Qt.CursorShape.ArrowCursor
        )

    def _colocar(self, item: BaseComponente, pos: QPointF | None) -> None:
        if pos is None:
            pos = QPointF(0, 0)
        punto = snap_a_grilla(pos.x(), pos.y(), TAMANO_GRILLA)
        item.setPos(punto.x * TAMANO_GRILLA, punto.y * TAMANO_GRILLA)
        self.scene.addItem(item)
        self.circuito_cambiado.emit()

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_R:
            self.agregar_resistencia(pos=self._pos_centro())
        elif event.key() == Qt.Key.Key_V:
            self.agregar_fuente(pos=self._pos_centro())
        elif event.key() == Qt.Key.Key_T:
            self._rotar_seleccion()
        elif event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self._eliminar_seleccion()
        else:
            super().keyPressEvent(event)

    def _rotar_seleccion(self, grados: float = 90.0) -> None:
        """Rota 90° el componente seleccionado para permitir ramas verticales."""
        rotado = False
        for item in self.scene.selectedItems():
            if isinstance(item, BaseComponente):
                item.setRotation((item.rotation() + grados) % 360)
                rotado = True
        if rotado:
            self._actualizar_resaltado()
            self._reconstruir_cables()
            self.circuito_cambiado.emit()

    def _pos_centro(self) -> QPointF:
        return self.mapToScene(self.viewport().rect().center())

    def _eliminar_seleccion(self) -> None:
        borrado = False
        eliminados: set[BaseComponente] = set()
        for item in self.scene.selectedItems():
            if isinstance(item, BaseComponente):
                eliminados.add(item)
                self.scene.removeItem(item)
                borrado = True
        if not borrado:
            return
        if self._terminal_pendiente is not None and self._terminal_pendiente[0] in eliminados:
            self._terminal_pendiente = None
            self._actualizar_resaltado()
        self._reconstruir_cables()
        self.circuito_cambiado.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self._procesar_clic_derecho(event.position())
            return
        if self._modo_conexion and event.button() == Qt.MouseButton.LeftButton:
            self._procesar_clic_conexion(event.position())
            return
        super().mousePressEvent(event)

    def _procesar_clic_derecho(self, pos_viewport: QPointF) -> None:
        """Clic derecho sobre un terminal/nodo -> marcar como tierra (0 V)."""
        punto = self.mapToScene(pos_viewport.toPoint())
        terminal = self._terminal_mas_cercano(punto, tolerancia=24.0)
        if terminal is not None:
            item, idx = terminal
            punto = item.terminales_escena()[idx]
            self.marcar_tierra_en(punto)
            return
        # Sobre un nodo existente (celda con terminales) o un punto vacío.
        self.marcar_tierra_en(punto)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self._aplicar_iman_y_cables()

    def _aplicar_iman_y_cables(self) -> None:
        """Al soltar un componente, lo imanta a un terminal cercano y redibuja cables."""
        self._imantar_componentes()
        self._actualizar_resaltado()
        self._reconstruir_cables()
        self.circuito_cambiado.emit()

    def _imantar_componentes(self, radio: float = 6.0) -> None:
        """Atrae terminales sueltos hacia terminales cercanos de otros componentes."""
        for item in self.componentes():
            for idx in (0, 1):
                tp = item.terminales_escena()[idx]
                vecino = self._terminal_de_otro(item, tp, radio)
                if vecino is not None:
                    item.setPos(item.pos() + (vecino - tp))

    def _procesar_clic_conexion(self, pos_viewport: QPointF) -> None:
        punto = self.mapToScene(pos_viewport.toPoint())
        terminal = self._terminal_mas_cercano(punto)
        if terminal is None:
            # Clic en vacío: cancela la selección pendiente.
            self._terminal_pendiente = None
            self._actualizar_resaltado()
            return
        if self._terminal_pendiente is None:
            self._terminal_pendiente = terminal
        elif self._terminal_pendiente[0] is terminal[0]:
            # Clic en el mismo componente: cancela.
            self._terminal_pendiente = None
        else:
            self._agregar_conexion(self._terminal_pendiente, terminal)
            self._terminal_pendiente = None
        self._actualizar_resaltado()
        self._reconstruir_cables()
        self.circuito_cambiado.emit()

    def _agregar_conexion(
        self,
        a: tuple[BaseComponente, int],
        b: tuple[BaseComponente, int],
    ) -> None:
        """Registra una conexión explícita por cable (sin duplicados)."""
        normalizada = tuple(sorted((a, b), key=lambda t: (id(t[0]), t[1])))
        if normalizada in self._conexiones:
            return
        self._conexiones.append(normalizada)

    def _conexiones_como_ids(self) -> list[tuple[str, str]]:
        """Traduce las conexiones a pares de ids de terminal del detector."""
        etiqueta = {0: "a", 1: "b"}
        return [
            (f"{a[0].id_comp}:{etiqueta[a[1]]}", f"{b[0].id_comp}:{etiqueta[b[1]]}")
            for a, b in self._conexiones
        ]

    def _actualizar_resaltado(self) -> None:
        if self._resaltado is not None:
            self.scene.removeItem(self._resaltado)
            self._resaltado = None
        if self._terminal_pendiente is None:
            return
        item, idx = self._terminal_pendiente
        self._resaltado = TerminalResaltadoItem(item.terminales_escena()[idx])
        self.scene.addItem(self._resaltado)

    def borrar_todos_los_cables(self) -> None:
        """Elimina todas las conexiones explícitas y sus cables."""
        self._conexiones.clear()
        self._terminal_pendiente = None
        self._actualizar_resaltado()
        self._reconstruir_cables()
        self.circuito_cambiado.emit()

    def _terminal_mas_cercano(
        self, punto: QPointF, tolerancia: float = 16.0
    ) -> tuple[BaseComponente, int] | None:
        mejor = None
        mejor_dist = tolerancia
        for item in self.componentes():
            ta, tb = item.terminales_escena()
            for indice, tp in enumerate((ta, tb)):
                dist = QLineF(punto, tp).length()
                if dist <= mejor_dist:
                    mejor = (item, indice)
                    mejor_dist = dist
        return mejor

    def _terminal_de_otro(
        self, item: BaseComponente, punto: QPointF, tolerancia: float
    ) -> QPointF | None:
        """Punto del terminal más cercano que pertenezca a otro componente."""
        mejor = None
        mejor_dist = tolerancia
        for otro in self.componentes():
            if otro is item:
                continue
            ta, tb = otro.terminales_escena()
            for tp in (ta, tb):
                dist = QLineF(punto, tp).length()
                if dist <= mejor_dist:
                    mejor = tp
                    mejor_dist = dist
        return mejor

    def _reconstruir_cables(self) -> None:
        """
        Redibuja los cables visibles:
        1. Conexiones explícitas creadas con el modo cable (líneas rectas
           entre los terminales actuales de cada extremo).
        2. Terminales que comparten celda de grilla (comportamiento de imán).
        """
        for cable in self._cables:
            self.scene.removeItem(cable)
        self._cables.clear()

        # Limpia conexiones cuyos componentes ya no existen en la escena.
        vivos = set(self.componentes())
        self._conexiones = [
            (a, b)
            for a, b in self._conexiones
            if a[0] in vivos and b[0] in vivos
        ]

        # 1. Cables explícitos.
        for (item_a, idx_a), (item_b, idx_b) in self._conexiones:
            tp_a = item_a.terminales_escena()[idx_a]
            tp_b = item_b.terminales_escena()[idx_b]
            self._agregar_cable(tp_a, tp_b)

        # 2. Terminales que comparten celda de grilla.
        grupos: dict[tuple[int, int], list[QPointF]] = {}
        for item in self.componentes():
            ta, tb = item.terminales_escena()
            for tp in (ta, tb):
                celda = snap_a_grilla(tp.x(), tp.y(), TAMANO_GRILLA)
                grupos.setdefault((celda.x, celda.y), []).append(tp)
        if self._nodo_tierra is not None:
            clave = (self._nodo_tierra.x, self._nodo_tierra.y)
            grupos.setdefault(clave, []).append(
                QPointF(
                    self._nodo_tierra.x * TAMANO_GRILLA,
                    self._nodo_tierra.y * TAMANO_GRILLA,
                )
            )
        for puntos in grupos.values():
            if len(puntos) < 2:
                continue
            hub = puntos[0]
            for tp in puntos[1:]:
                self._agregar_cable(hub, tp)

    def _agregar_cable(self, origen: QPointF, destino: QPointF) -> None:
        if QLineF(origen, destino).length() < 1.0:
            return
        cable = CableItem(origen, destino)
        self.scene.addItem(cable)
        self._cables.append(cable)

    def _on_selection_changed(self) -> None:
        seleccion = self.scene.selectedItems()
        if seleccion and isinstance(seleccion[0], BaseComponente):
            self.componente_seleccionado.emit(seleccion[0])

    def drawBackground(self, painter: QPainter, rect):
        super().drawBackground(painter, rect)
        left = int(rect.left()) - (int(rect.left()) % TAMANO_GRILLA)
        top = int(rect.top()) - (int(rect.top()) % TAMANO_GRILLA)
        pen = QPen(QColor("#2A2A2A"), 0)
        painter.setPen(pen)
        x = left
        while x < rect.right():
            painter.drawLine(QLineF(x, rect.top(), x, rect.bottom()))
            x += TAMANO_GRILLA
        y = top
        while y < rect.bottom():
            painter.drawLine(QLineF(rect.left(), y, rect.right(), y))
            y += TAMANO_GRILLA
