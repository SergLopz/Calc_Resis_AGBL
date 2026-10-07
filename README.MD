# Calculadora Visual e Interactiva de Circuitos Resistivos

[![Python](https://img.shields.io/badge/Python-3.14%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/GUI-PyQt6-green?logo=qt)](https://www.qt.io/)
[![Package Manager](https://img.shields.io/badge/package_manager-uv-purple?logo=astral)](https://astral.sh/uv/)
[![Linter](https://img.shields.io/badge/code_style-Ruff-red?logo=ruff)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Aplicación de escritorio multiplataforma para el diseño, simulación interactiva y análisis topológico de circuitos eléctricos DC. Desarrollada por el grupo **"Juiciosos" - Primer semestre UCompensar** como un entorno educativo que automatiza el análisis por mallas, clasifica nodos según su grado topológico y presenta las matrices resultantes en notación matemática rigurosa $\LaTeX$.

---

## 📑 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Pila Tecnológica](#-pila-tecnológica)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Licencia](#-licencia)

---

## 🔍 Descripción General

El análisis manual de circuitos eléctricos mediante las Leyes de Kirchhoff (LVK y LCK) es propenso a errores en la identificación de recorridos cerrados independientes y la formulación matricial. Esta herramienta aborda dicho problema integrando:

1. **Un lienzo vectorial dinámico:** Permite construir esquemáticos de hasta **20 resistencias** y **3 fuentes de voltaje DC**.
2. **Motor de teoría de grafos:** Clasifica de forma autómata los nodos simples ($d(v) = 2$, letras minúsculas) y esenciales ($d(v) \geq 3$, letras mayúsculas).
3. **Módulo de álgebra lineal:** Determina la base de ciclos independientes tomando como pivote la fuente de mayor magnitud ($V_{\text{max}}$) y resuelve el sistema $\mathbf{R} \cdot \mathbf{I} = \mathbf{V}$ mediante descomposición numérica.

---

## ✨ Características Principales

* **Lienzo Gráfico Interactivo:** Arrastre de componentes, conexiones dinámicas y atajos de teclado (`R` para resistencia, `V` para fuente).
* **Renderización Matricial $\LaTeX$:** Visualización en tiempo real de las matrices $\mathbf{R}$, $\mathbf{I}$ y $\mathbf{V}$ generadas dinámicamente.
* **Inspección de Componentes:** Cálculo puntual de voltaje ($V_{R_x}$), corriente ($I_{R_x}$) y potencia disipada ($P_{R_x}$) por elemento.
* **Layout Adaptable (Responsive):** División de panales ajustable mediante `QSplitter` y tema de alto contraste para accesibilidad visual.

---

## 📐 Arquitectura del Sistema

El proyecto implementa el patrón **Model-View-Controller (MVC)** desacoplado mediante eventos y señales Qt:

```text
Calc_Resis_AGBL/
├── docs/                      # Documentación del proyecto y teoría de circuitos
├── src/
│   └── calc_resis_agbl/
│       ├── core/              # Lógica de negocio (NetworkX, NumPy Solver)
│       │   ├── graph_builder.py
│       │   └── solver.py
│       ├── models/            # Modelos de datos (Resistencia, FuenteDC, Circuito)
│       │   ├── componentes.py
│       │   └── circuito.py
│       ├── ui/                # Interfaz de usuario (PyQt6 GraphicsView & Splitter)
│       │   ├── canvas.py
│       │   ├── graphics_items.py
│       │   ├── main_window.py
│       │   └── matrix_panel.py
│       └── utils/             # Funciones auxiliares (Formateador LaTeX)
│           └── latex_renderer.py
├── tests/                     # Pruebas unitarias automatizadas (pytest)
└── pyproject.toml             # Configuración unificada (UV, Ruff, Proyecto)
```
---
## 🛠️ Pila Tecnológica
* Lenguaje: Python 3.11+

* Gestor de Proyecto y Entorno: uv (Astral)

* GUI & Lienzo Vectorial: PyQt6 (QGraphicsScene / QGraphicsView)

* Análisis de Grafos: NetworkX

* Álgebra Lineal: NumPy / SymPy

* Renderizado Matemático: Matplotlib (mathtext)

* Calidad de Código y Pruebas: Ruff & Pytest
---
## ⚙️ Requisitos Previos
Tener instalado el gestor ultra rápido `uv`. Si aún no lo tienes:
* Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"` 
* Linux / MacOS: `curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh`
---
## 🚀 Instalación y Configuración
1. Clonar el repositorio:
```Bash
git clone [https://github.com/SergLopz/Calc_Resis_AGBL.git](https://github.com/SergLopz/Calc_Resis_AGBL.git)
cd Calc_Resis_AGBL
```
2. Sincronizar el entorno de desarrollo:
```Bash
uv sync
```
3. Ejecutar la aplicación:
```Bash
uv run src/circuito_app/main.py
```
---
## 📄 Licencia
Este proyecto se distribuye bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más información.