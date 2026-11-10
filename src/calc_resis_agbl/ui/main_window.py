from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from calc_resis_agbl.core.mesh_solver import MeshSolver
from calc_resis_agbl.core.nodal_solver import NodalSolver
from calc_resis_agbl.models.circuito import Circuito
from calc_resis_agbl.models.componentes import CircuitoError
from calc_resis_agbl.ui.canvas import CircuitCanvas
from calc_resis_agbl.ui.matrix_panel import MatrixPanel


class MainWindow(QMainWindow):
    """Ventana principal: lienzo + controles + matrices + resultados."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora Visual de Circuitos - Grupo Juiciosos")
        self.resize(1300, 850)

        self.canvas = CircuitCanvas(self)
        self.canvas.circuito_cambiado.connect(self._on_circuito_cambiado)
        self.canvas.componente_seleccionado.connect(self._on_componente_seleccionado)

        ensamblado = QSplitter(Qt.Orientation.Horizontal)
        ensamblado.addWidget(self._panel_controles())
        ensamblado.addWidget(self.canvas)
        ensamblado.setSizes([300, 1000])

        derecho = QSplitter(Qt.Orientation.Vertical)
        derecho.addWidget(ensamblado)
        self.matrix_panel = MatrixPanel(self)
        self.matrix_panel.mostrar_mensaje(
            "Dibuja un circuito, marca tierra con clic derecho y presiona Resolver."
        )
        derecho.addWidget(self.matrix_panel)
        derecho.setSizes([500, 350])

        cuerpo = QSplitter(Qt.Orientation.Horizontal)
        cuerpo.addWidget(derecho)
        cuerpo.addWidget(self._panel_resultados())
        cuerpo.setSizes([900, 400])

        self.setCentralWidget(cuerpo)
        self.statusBar().showMessage(self._texto_ayuda())

    # ------------------------------------------------------------------
    # Construcción de paneles
    # ------------------------------------------------------------------
    def _panel_controles(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        grupo_add = QGroupBox("Agregar componente")
        form = QFormLayout(grupo_add)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Resistencia (R)", "Fuente DC (V)"])
        self.valor_spin = QDoubleSpinBox()
        self.valor_spin.setRange(0.001, 1e9)
        self.valor_spin.setValue(1000.0)
        self.valor_spin.setDecimals(3)
        self.valor_spin.setSuffix(" Ω")

        boton_add = QPushButton("Agregar al lienzo")
        boton_add.clicked.connect(self._agregar_componente)

        form.addRow("Tipo:", self.tipo_combo)
        form.addRow("Valor:", self.valor_spin)
        form.addRow(boton_add)
        self.tipo_combo.currentIndexChanged.connect(self._actualizar_unidad)

        grupo_metodo = QGroupBox("Método de análisis")
        form_m = QFormLayout(grupo_metodo)
        self.metodo_combo = QComboBox()
        self.metodo_combo.addItems(
            ["Análisis por Mallas (R·I=V)", "Análisis Nodal (MNA)"]
        )
        form_m.addRow("Método:", self.metodo_combo)

        boton_resolver = QPushButton("Resolver circuito")
        boton_resolver.setStyleSheet("font-weight: bold; padding: 6px;")
        boton_resolver.clicked.connect(self._resolver)

        self.boton_modo_cable = QPushButton("Modo cable")
        self.boton_modo_cable.setCheckable(True)
        self.boton_modo_cable.toggled.connect(self.canvas.activar_modo_conexion)

        boton_borrar_cables = QPushButton("Borrar cables")
        boton_borrar_cables.clicked.connect(self.canvas.borrar_todos_los_cables)

        boton_limpiar = QPushButton("Limpiar todo")
        boton_limpiar.clicked.connect(self.canvas.limpiar)

        boton_tierra = QPushButton("Quitar tierra")
        boton_tierra.clicked.connect(self.canvas.limpiar_tierra)

        layout.addWidget(grupo_add)
        layout.addWidget(grupo_metodo)
        layout.addWidget(boton_resolver)
        layout.addWidget(self.boton_modo_cable)
        layout.addWidget(boton_borrar_cables)
        layout.addWidget(boton_tierra)
        layout.addWidget(boton_limpiar)
        layout.addStretch(1)
        return panel

    def _panel_resultados(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        grupo_mallas = QGroupBox("Mallas detectadas")
        layout_mallas = QVBoxLayout(grupo_mallas)
        self.leyenda_mallas = QTextBrowser()
        self.leyenda_mallas.setMaximumHeight(150)
        self.leyenda_mallas.setStyleSheet(
            "background:#252526;color:#CCCCCC;border:1px solid #444;padding:4px;"
        )
        self.leyenda_mallas.setHtml(
            "Resuelve por mallas para ver la numeración M1..Mn."
        )
        layout_mallas.addWidget(self.leyenda_mallas)
        layout.addWidget(grupo_mallas)

        layout.addWidget(QLabel("<b>Resultados por componente</b>"))
        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Tipo", "Corriente (A)", "Voltaje (V)", "Potencia (W)"]
        )
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla)

        self.inspeccion = QLabel("Selecciona un componente del lienzo.")
        self.inspeccion.setWordWrap(True)
        self.inspeccion.setStyleSheet(
            "background:#252526;color:#00FFCC;padding:8px;border:1px solid #444;"
        )
        layout.addWidget(self.inspeccion)
        return panel

    # ------------------------------------------------------------------
    # Lógica
    # ------------------------------------------------------------------
    def _texto_ayuda(self) -> str:
        return (
            "R/V: agregar · T: rotar · Supr: borrar · clic derecho: marcar tierra "
            "(0 V) · 'Modo cable': clic en un terminal y luego en otro para unirlos."
        )

    def _actualizar_unidad(self):
        es_resistencia = self.tipo_combo.currentIndex() == 0
        self.valor_spin.setSuffix(" Ω" if es_resistencia else " V")
        if es_resistencia:
            self.valor_spin.setValue(1000.0)
        else:
            self.valor_spin.setValue(12.0)

    def _agregar_componente(self):
        valor = self.valor_spin.value()
        if self.tipo_combo.currentIndex() == 0:
            self.canvas.agregar_resistencia(valor)
        else:
            self.canvas.agregar_fuente(valor)

    def _on_circuito_cambiado(self):
        self.matrix_panel.mostrar_mensaje(
            "Circuito modificado. Presiona Resolver para recalcular."
        )
        self.leyenda_mallas.setHtml(
            "Circuito modificado. Resuelve para actualizar las mallas."
        )

    def _construir_circuito(self) -> Circuito:
        componentes = self.canvas.construir_componentes_modelo()
        circuito = Circuito()
        for comp in componentes:
            if hasattr(comp, "nodo_a"):
                circuito.agregar_resistencia(comp)
            else:
                circuito.agregar_fuente(comp)
        return circuito

    def _resolver(self):
        circuito = self._construir_circuito()
        try:
            circuito.validar()
            if self.canvas.id_nodo_tierra() is None:
                raise CircuitoError(
                    "Marca un nodo de tierra con clic derecho antes de resolver."
                )
            if self.metodo_combo.currentIndex() == 0:
                resultado = MeshSolver().resolver(circuito.obtener_todos_los_componentes())
                self._mostrar_matriz_mallas(resultado)
                self._mostrar_leyenda_mallas(resultado)
            else:
                resultado = NodalSolver().resolver(circuito.obtener_todos_los_componentes())
                self._mostrar_matriz_nodal(resultado)
                self._mostrar_leyenda_nodal()
        except CircuitoError as ex:
            QMessageBox.warning(self, "No se pudo resolver", str(ex))
            return
        except Exception as ex:  # noqa: BLE001 - se muestra al usuario
            QMessageBox.critical(self, "Error inesperado", repr(ex))
            return

        self._mostrar_resultados(resultado["componentes"])
        self.statusBar().showMessage(f"Resuelto con {resultado['metodo']}.")

    def _mostrar_matriz_mallas(self, resultado: dict) -> None:
        mallas = resultado["mallas"]
        etiquetas = [malla["id"] for malla in mallas]
        incognitas = [f"I_{malla['id']}" for malla in mallas]
        self.matrix_panel.mostrar_sistema(
            resultado["matriz_r"],
            incognitas,
            resultado["vector_v"],
            titulo="Análisis por mallas: R · I = V",
            solucion=resultado["vector_i"],
            nombres=("R (Ω)", "I (A)", "V (V)"),
            etiquetas_filas=etiquetas,
            etiquetas_columnas=etiquetas,
            unidad_solucion="A",
        )

    def _mostrar_matriz_nodal(self, resultado: dict) -> None:
        solucion = resultado["solucion"]
        incognitas = [f"x{k + 1}" for k in range(len(solucion))]
        filas = [f"Ec. {k + 1}" for k in range(len(solucion))]
        self.matrix_panel.mostrar_sistema(
            resultado["matriz_a"],
            incognitas,
            resultado["vector_b"],
            titulo="Análisis nodal MNA: A · x = b",
            solucion=solucion,
            nombres=("A", "x", "b"),
            etiquetas_filas=filas,
            etiquetas_columnas=incognitas,
            unidad_solucion="",
        )

    def _mostrar_leyenda_mallas(self, resultado: dict) -> None:
        self.leyenda_mallas.setHtml(self._html_leyenda_mallas(resultado))

    def _mostrar_leyenda_nodal(self) -> None:
        self.leyenda_mallas.setHtml(
            "El análisis nodal no usa mallas: las incógnitas son las tensiones "
            "de nodo y las corrientes de las fuentes."
        )

    @staticmethod
    def _html_leyenda_mallas(resultado: dict) -> str:
        grupos = resultado.get("paralelos", {})
        etiqueta_paralelo: dict[str, str] = {}
        for grupo in grupos.values():
            texto = " || ".join(grupo["ids"]) + f" = {grupo['valor_eq']:.6g} Ω"
            for comp_id in grupo["ids"]:
                etiqueta_paralelo[comp_id] = texto

        lineas = []
        for malla in resultado.get("mallas", []):
            componentes = []
            vistos = set()
            for comp_id in malla.get("componentes", []):
                texto = etiqueta_paralelo.get(comp_id, comp_id)
                if texto not in vistos:
                    vistos.add(texto)
                    componentes.append(texto)
            lineas.append(
                f"<b>{malla['id']}</b> ({malla.get('sentido', 'indefinido')}): "
                + ", ".join(componentes)
            )
        if not lineas:
            return "No se detectaron mallas."
        return "<br>".join(lineas)

    def _mostrar_resultados(self, componentes: list[dict]) -> None:
        self.tabla.setRowCount(len(componentes))
        for fila, comp in enumerate(componentes):
            valores = [
                comp["id"],
                comp["tipo"],
                f"{comp['corriente']:.6g}",
                f"{comp['voltaje']:.6g}",
                f"{comp['potencia']:.6g}",
            ]
            for col, texto in enumerate(valores):
                self.tabla.setItem(fila, col, QTableWidgetItem(texto))

    def _on_componente_seleccionado(self, item):
        filas = self.tabla.rowCount()
        for fila in range(filas):
            celda_id = self.tabla.item(fila, 0)
            if celda_id and celda_id.text() == item.id_comp:
                self.inspeccion.setText(
                    f"<b>{item.id_comp}</b> ({item.valor:g}) — "
                    f"I={self.tabla.item(fila, 2).text()} A · "
                    f"V={self.tabla.item(fila, 3).text()} V · "
                    f"P={self.tabla.item(fila, 4).text()} W"
                )
                return
