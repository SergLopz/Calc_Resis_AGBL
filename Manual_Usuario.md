# Manual de Usuario — Calculadora Visual de Circuitos Resistivos

**Proyecto:** Calculadora de Circuitos Resistivos DC
**Equipo:** Grupo "Juiciosos" — UCompensar
**Versión:** 1.1

---

## 1. ¿Qué hace esta aplicación?

Permite **dibujar** un circuito resistivo de corriente directa (DC) en un lienzo
interactivo, **detectar automáticamente los nodos**, y **resolverlo** mediante
dos métodos de análisis de circuitos:

- **Análisis por Mallas** (Ley de Tensiones de Kirchhoff, `R · I = V`).
- **Análisis Nodal** (Método de Nodos / MNA, `A · x = b`).

Los resultados (corriente, voltaje y potencia por componente) se muestran en una
tabla, junto con el sistema de ecuaciones matricial que se resolvió.

**Alcance:** solo circuitos **resistivos DC** (resistencias y fuentes de voltaje
continuo). No soporta AC, capacitores ni inductores.

**Límites del proyecto:** máximo **20 resistencias** y **3 fuentes DC** por circuito.

---

## 2. Requisitos e instalación

- Python **3.11 o superior**.
- Gestor de paquetes **`uv`** (recomendado).

```bash
# Instalar dependencias y crear el entorno
uv sync
```

---

## 3. Cómo ejecutar la aplicación

```bash
uv run src/calc_resis_agbl/main.py
```

O, tras `uv sync`, mediante el script instalado:

```bash
uv run calc-resis-agbl
```

---

## 4. Interfaz de la ventana

La ventana se divide en cuatro zonas:

1. **Panel de controles (izquierda):** agregar componentes, elegir método,
   resolver, quitar tierra y limpiar.
2. **Lienzo (centro):** donde se dibuja y conecta el circuito sobre una grilla.
3. **Panel de matrices (abajo):** muestra el sistema de ecuaciones del método
   elegido como matrices apiladas (`R =`, `I =`, `V =` o `A =`, `x =`, `b =`).
4. **Panel de resultados (derecha):** leyenda de **"Mallas detectadas"**, tabla
   con `ID`, `Tipo`, `Corriente`, `Voltaje` y `Potencia`, más un cuadro de
   inspección del componente seleccionado.

---

## 5. Flujo de trabajo paso a paso

### Paso 1 — Agregar componentes
- Selecciona el **Tipo** (Resistencia o Fuente DC) y el **Valor** en el panel
  izquierdo (el valor de una resistencia está en **Ω** y el de una fuente en **V**).
- Presiona **"Agregar al lienzo"**, o usa los atajos:
  - **`R`** → agrega una resistencia.
  - **`V`** → agrega una fuente DC.

### Paso 2 — Ubicar y conectar
- **Arrastra** los componentes sobre la grilla.
- Al soltar un componente cerca del terminal de otro, se **conecta
  automáticamente por "imán"**. Dos terminales que caen en la **misma celda de
  la grilla** forman un **mismo nodo eléctrico**.
- Para ramas verticales, selecciona el componente y presiona **`T`** para
  **rotarlo 90°**.

### Paso 2b — Conectar con "Modo cable" (unir componentes separados)
Cuando los componentes están **separados** (como en un esquemático normal) y
sus terminales **no coinciden** en la misma celda, usa el botón **"Modo cable"**
para tender cables que los unan:

1. Presiona el botón **"Modo cable"** (queda activo; el cursor cambia a cruz).
   El modo es **persistente** hasta que lo desactives.
2. Haz **clic** sobre el terminal de un componente. Se resalta con un círculo.
3. Haz **clic** sobre el terminal de otro componente. Aparece un **cable**
   (línea recta) que los une y ambos terminales pasan a ser **el mismo nodo**.
4. Repite para el resto de las uniones. Clic en una zona vacía **cancela** la
   selección pendiente.
5. Desactiva el botón **"Modo cable"** cuando termines.
6. El botón **"Borrar cables"** elimina todas las conexiones por cable de una vez.

> También puedes **combinar** ambos mecanismos: el imán (superponer terminales)
> y el modo cable (tender un cable entre terminales separados).

### Paso 3 — Definir la tierra (nodo de referencia)
- Haz **clic derecho** sobre un terminal o nodo.
- Se marca como **tierra (0 V)** y aparece un símbolo de tierra.
- Toda resolución **requiere** que exista un nodo de referencia.
- Para eliminarla, usa el botón **"Quitar tierra"**.

### Paso 4 — Elegir el método y resolver
- En **"Método de análisis"** elige **Análisis por Mallas** o **Análisis Nodal**.
- Presiona **"Resolver circuito"**.
- Si el circuito es válido, verás:
  - El **sistema matricial** en el panel inferior.
  - La **tabla de resultados** por componente.

### Paso 5 — Inspeccionar resultados
- La tabla lista cada elemento con su **corriente (A)**, **voltaje (V)** y
  **potencia (W)**.
- **Haz clic en un componente del lienzo** para ver un resumen destacado en el
  cuadro de inspección.

---

## 6. Atajos de teclado

| Tecla                  | Acción                                            |
| ---------------------- | ------------------------------------------------- |
| `R`                    | Agregar una resistencia                           |
| `V`                    | Agregar una fuente DC                             |
| `T`                    | Rotar 90° el componente seleccionado              |
| `Supr` / `Retroceso`   | Borrar el componente seleccionado                 |
| **Clic derecho**       | Marcar el nodo/terminal bajo el cursor como tierra |

> El botón **"Modo cable"** (persistente) habilita la conexión por
> **dos clics** en terminales; **"Borrar cables"** limpia esas conexiones.

---

## 7. Cómo se detectan los nodos

La aplicación **no** necesita que indiques los nodos manualmente:

- Cada **terminal** ocupa una celda de la grilla.
- Los terminales que comparten la **misma celda** se agrupan en un **nodo**.
- Los terminales unidos por un **cable explícito** (Modo cable) forman también
  un **mismo nodo**, aunque estén en celdas distintas.
- Los nodos se **clasifican automáticamente** por su grado (número de conexiones):
  - **Grado 2** (nodo *simple*) → letra **minúscula** (a, b, c…).
  - **Grado ≥ 3** (nodo *esencial*) → letra **mayúscula** (A, B, C…).
  - El nodo marcado como **tierra** se identifica como **`0`** (referencia).

---

## 8. Cómo leer las matrices

El panel inferior muestra **tres matrices apiladas** con la forma del sistema
resuelto:

```text
R = [ ... ]      (matriz de coeficientes)
I = [ ... ]      (vector de incógnitas)
V = [ ... ]      (vector de términos independientes)
```

Debajo aparece la línea **`Solución:`** con el valor numérico de cada incógnita.
Si el sistema es grande, el panel permite desplazarse vertical y horizontalmente.

### Análisis por Mallas

Se resuelve el sistema **`R · I = V`**, donde:

- **`R`** es la matriz de resistencias. La diagonal contiene la suma de las
  resistencias de cada malla; fuera de la diagonal, la resistencia compartida
  entre dos mallas (con signo negativo).
- **`I`** es el vector de corrientes de malla, con incógnitas **`I_M1, I_M2, …`**.
- **`V`** es el vector de fuentes de voltaje aportadas a cada malla.

Las filas y columnas se rotulan **`M1, M2, …`**, de modo que la fila `M1`
corresponde a la ecuación de la malla 1 y la columna `M1` a su corriente.

**Numeración y sentido de las mallas:**

- Se detectan las **ventanas geométricas** que se ven en el dibujo (las caras
  interiores del circuito), no una base arbitraria de ciclos.
- **`M1`** es la ventana ubicada más abajo y, dentro de una misma fila, la más
  **a la izquierda**; luego se numera de izquierda a derecha y de abajo hacia
  arriba.
- Todas las mallas se recorren en **sentido horario**.
- Los **puentes** (ramas que no forman parte de ninguna ventana) no se asignan
  a ninguna malla. Las ventanas **anidadas** se detectan por separado.
- La leyenda **"Mallas detectadas"** del panel derecho lista cada malla con su
  sentido y sus componentes, por ejemplo:
  `M1 (horario): V1, R1, R2, R3`.

> **Resistencias en paralelo:** si dos o más resistencias comparten exactamente
> los mismos dos nodos, el método las trata como su **equivalente** para mallar
> y luego reparte la corriente entre ellas (comparten la misma tensión). En la
> matriz aparece el valor equivalente y la leyenda lo anota como
> `R2 || R3 = 250 Ω`. El resultado coincide con el método Nodal.

### Análisis Nodal (MNA)

Se resuelve el sistema **`A · x = b`**, donde:

- **`A`** es la matriz de conductancias y conexiones de la red.
- **`x`** contiene las **tensiones de nodo** respecto a la tierra (y las
  corrientes por las fuentes).
- **`b`** es el vector de términos independientes.

Las filas se rotulan **`Ec. 1, Ec. 2, …`** y las columnas **`x1, x2, …`**. La
leyenda indica que el método nodal no utiliza mallas.

---

## 9. Solución de problemas

| Mensaje / situación                                            | Causa y solución                                                                 |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| "Incluye el nodo de referencia '0' (tierra)..."                | No marcaste tierra. Haz **clic derecho** en un nodo y vuelve a resolver.          |
| "El circuito necesita al menos dos nodos distintos."           | El circuito está incompleto o todos los terminales caen en una sola celda.        |
| "El grafo tiene nodos desconectados..."                        | Hay ramas aisladas. Únelas con **Modo cable** o el imán de terminales.            |
| "No se detectaron mallas independientes..."                    | No hay ningún lazo cerrado. Cierra el circuito.                                   |
| "Se alcanzó el límite de 20 resistencias."                     | Superaste el máximo del proyecto. Elimina elementos (selecciona + `Supr`).        |
| "Se alcanzó el límite de 3 fuentes DC."                        | Superaste el máximo de fuentes. Elimina alguna fuente.                            |
| La tabla queda vacía tras resolver                             | Corrige la causa indicada en el mensaje de error y vuelve a presionar "Resolver". |

---

## 10. Buenas prácticas para dibujar bien

- Mantén los componentes **alineados a la grilla** (el imán lo hace por ti):
  si prefieres dibujar separado, usa **Modo cable** para unir los terminales.
- Recuerda que **solo los terminales en la misma celda se unen por imán**; un
  "casi contacto" que no coincide en celda **no** crea un nodo (usa el cable).
- Marca la tierra en un nodo que ya forme parte del circuito.
- Usa `T` para alternar entre orientación horizontal y vertical y cerrar lazos.

---

## 11. Verificación del proyecto (desarrollo)

El proyecto incluye pruebas automatizadas:

```bash
uv run pytest -q        # Ejecuta la batería de pruebas
uv run ruff check src tests   # Verifica estilo y errores estáticos
```

Las pruebas cubren: núcleo matemático (mallas ≡ nodal, incluido el paralelo),
extracción geométrica de ventanas (numeración, sentido horario, puentes,
anidados y fallback), formato de las matrices, leyenda de mallas, detección de
nodos y snapping, integración desde el lienzo, conexiones por cable, límites
(20 R / 3 V) y validaciones de errores de conexión.

---

> Para más detalles técnicos y de arquitectura, consulta
> `mate_add/PLAN_DESARROLLO.md`.
