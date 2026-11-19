# Guion de exposición — Calculadora Visual de Circuitos Resistivos

> **Duración objetivo:** 10 minutos (máximo 15).
> **Reparto:** 5 personas, aproximadamente 2 minutos cada una.
> **Eje central:** el álgebra lineal como puente entre el circuito y la solución.
> **Regla de oro:** este documento es un guion de apoyo; no se debe leer literalmente frente al público.

---

## 0. Antes de empezar

### Hilo conductor de toda la exposición

1. Un circuito resistivo se puede describir con **ecuaciones lineales**.
2. Esas ecuaciones se organizan en una **matriz de coeficientes**, un **vector de incógnitas** y un **vector de términos independientes**.
3. La geometría del dibujo permite elegir una **base del espacio de ciclos** (las mallas).
4. El sistema se resuelve con **métodos numéricos** (`np.linalg.solve`, basado en LU).
5. La solución es un **vector**; de él se derivan corrientes, voltajes y potencias por componente.

### Reparto y tiempos

| Persona | Tiempo | Tema | Slides sugeridos |
| :--- | :--- | :--- | :--- |
| **Persona 1** | 0:00 – 2:00 | Apertura: el circuito como sistema de ecuaciones | 1–2 |
| **Persona 2** | 2:00 – 4:00 | De Kirchhoff a `R · I = V` | 3–4 |
| **Persona 3** | 4:00 – 6:00 | Geometría, grafos y espacio de ciclos | 5–6 |
| **Persona 4** | 6:00 – 8:00 | Ensamblado de la matriz, casos especiales y solución | 7–8 |
| **Persona 5** | 8:00 – 10:00 | Demo, arquitectura, resultados y cierre | 9–10 |

> Si la exposición se extiende a 15 minutos, cada persona añade aproximadamente 1 minuto con las ideas opcionales de la sección 7.

### Material de apoyo

- Aplicación abierta con un circuito de ejemplo ya armado.
- Capturas de respaldo en `docs/images/`:
  - `UI.png` (interfaz general)
  - `lienzo.png` (circuito dibujado)
  - `matrices_mallas.png` (matrices `R`, `I`, `V`)
  - `leyenda_mallas.png` (mallas `M1..Mn`)
  - `resultados.png` (tabla de resultados)
- Manual de usuario: `Manual_Usuario.md`.
- Cronómetro visible para el equipo, no para el público.

### Acuerdo del equipo

- Cada persona termina con una frase de transición hacia la siguiente.
- Si alguien se pasa del tiempo, el siguiente retoma sin pedir disculpas.
- Si la demo falla, se usan las capturas y se continúa con el guion.
- No se leen las diapositivas: se explican con palabras propias.

---

## 1. Persona 1 — Apertura: el circuito es un sistema de ecuaciones

**Tiempo:** 0:00 – 2:00
**Slides:** 1–2
**Objetivo:** captar la atención, presentar el proyecto y declarar la tesis: el fundamento es álgebra lineal.

### Guion

> Buenos días. Somos el grupo **Juiciosos**, de UCompensar, y les presentamos nuestra **Calculadora Visual de Circuitos Resistivos**.
>
> La idea general es sencilla: el usuario dibuja un circuito en pantalla, la aplicación detecta los nodos y las ramas, y calcula corrientes, voltajes y potencias. Pero hoy queremos contarles algo más profundo: **por qué este proyecto es, en el fondo, un proyecto de álgebra lineal**.
>
> Un circuito resistivo parece un dibujo. Para una persona, es un conjunto de componentes conectados. Para la computadora, en cambio, es un **sistema de ecuaciones lineales**. Cada lazo, cada nodo y cada resistencia producen una ecuación; esas ecuaciones se escriben como una matriz por un vector.
>
> Nuestra aplicación hace visible ese proceso. No solo muestra el resultado: muestra la matriz `R`, el vector de incógnitas `I` y el vector de fuentes `V`. Y lo hace con valores numéricos reales, no con expresiones simbólicas.
>
> Ese detalle es importante para nosotros como estudiantes: en clase resolvemos sistemas de dos o tres ecuaciones a mano; aquí el mismo concepto se aplica a un circuito dibujado por el usuario, con más incógnitas y con una interfaz que permite comprobar cada paso. El proyecto, entonces, no es solo una calculadora: es una forma de ver el álgebra lineal funcionando.
>
> La pregunta que guía toda la exposición es esta: **¿cómo pasa un circuito dibujado a una matriz que se puede resolver?** La respuesta tiene tres partes: las leyes de Kirchhoff, la geometría del circuito y los métodos numéricos del álgebra lineal. Empecemos por la primera.

### Apoyo visual

- Mostrar `docs/images/UI.png` o la aplicación abierta.
- Señalar el lienzo, el panel de matrices y la tabla de resultados.

### Transición

> Para construir la matriz necesitamos las leyes de Kirchhoff. Eso se lo dejo a mi compañero/a.

### Si hay poco tiempo

> Decir solo: “El circuito se convierte en un sistema lineal; nuestra app muestra la matriz, no solo el resultado”.

---

## 2. Persona 2 — De Kirchhoff a `R · I = V`

**Tiempo:** 2:00 – 4:00
**Slides:** 3–4
**Objetivo:** explicar el análisis por mallas y la estructura de la matriz `R`.

### Guion

> Gracias. Yo les explico cómo se construye el sistema **`R · I = V`**.
>
> En el análisis por mallas, la incógnita no es la corriente de cada rama, sino la **corriente de cada malla**, es decir, de cada ventana del circuito. Recorremos cada malla en sentido horario y aplicamos la Ley de Tensiones de Kirchhoff: la suma de caídas de tensión alrededor de la malla es igual a las subidas producidas por las fuentes.
>
> Para que se vea concreto, tomen dos mallas que comparten una resistencia. La malla 1 tiene una fuente de 12 V, una resistencia de 1 kΩ y comparte con la malla 2 una resistencia de 2 kΩ. La malla 2 tiene una resistencia de 3 kΩ y la misma resistencia compartida de 2 kΩ.
>
> Si escribimos las ecuaciones y agrupamos las incógnitas, obtenemos:
>
> ```text
> [ 3  -2 ] [ I1 ]   [ 12 ]
> [ -2  5 ] [ I2 ] = [  0 ]
> ```
>
> Trabajamos en kΩ y mA para que los números sean legibles; es equivalente a ohmios y amperios.
>
> Miren la estructura: en la diagonal está la suma de las resistencias de cada malla: 1 + 2 = 3, y 2 + 3 = 5. Fuera de la diagonal está la resistencia compartida con signo negativo: −2. El vector de la derecha contiene las fuentes: 12 V en la malla 1 y 0 en la malla 2.
>
> La matriz es **simétrica**: el término de la fila 1, columna 2 es igual al de la fila 2, columna 1. Además, con resistencias positivas, es definida positiva. Su determinante es 11, distinto de cero, así que el sistema tiene solución única: `I1 = 5.45 mA` e `I2 = 2.18 mA`.
>
> Esa es la idea clave: **la matriz no es un adorno; es el modelo matemático del circuito**. Cada fila es una ecuación de malla, cada columna una incógnita y cada entrada una resistencia.

### Apoyo visual

- Mostrar la matriz de 2×2 y, si es posible, la misma estructura en la aplicación con un circuito de dos mallas.
- Señalar la simetría y la diagonal.

### Transición

> Pero queda una pregunta: ¿de dónde salen esas mallas? La aplicación no las pide; las descubre a partir del dibujo. Eso lo explica mi compañero/a.

### Si hay poco tiempo

> Omitir el ejemplo numérico y decir: “diagonal = suma de resistencias de la malla; fuera de diagonal = −resistencia compartida; el vector V contiene las fuentes”.

---

## 3. Persona 3 — Geometría, grafos y espacio de ciclos

**Tiempo:** 4:00 – 6:00
**Slides:** 5–6
**Objetivo:** explicar cómo se eligen las mallas y por qué eso es álgebra lineal.

### Guion

> Gracias. Yo respondo de dónde salen las mallas y por qué esa elección importa.
>
> La aplicación convierte el dibujo en un **grafo**: los terminales conectados son nodos y cada componente es una arista. Como el circuito se dibuja en un plano, ese grafo es planar. Las **caras interiores** del dibujo son exactamente las ventanas que una persona ve: esas son nuestras mallas.
>
> Hay un resultado de teoría de grafos que conecta esto con el álgebra lineal. Para un grafo conexo y planar, el número de mallas independientes es:
>
> ```text
> número de mallas = E − V + 1
> ```
>
> donde `E` es el número de aristas y `V` el número de vértices. Ese número es la **dimensión del espacio de ciclos**. En otras palabras: las mallas no son una lista arbitraria; son una **base** de ese espacio. Elegir las ventanas geométricas es elegir una base que el usuario puede interpretar.
>
> El algoritmo ordena los vecinos de cada nodo por ángulo, recorre las medias aristas y obtiene las caras. Luego calcula el área con signo para orientar cada ventana en sentido horario, y las numera `M1, M2, …` de abajo hacia arriba y de izquierda a derecha. Los puentes no pertenecen a ninguna malla; las ventanas anidadas se separan; y si el dibujo no es planar o falta geometría, se usan ciclos fundamentales como respaldo.
>
> ¿Por qué insistimos en esto? Porque **la base elegida determina la matriz**. Una base arbitraria produce una matriz correcta pero difícil de leer; una base geométrica produce una matriz que refleja las ventanas del circuito y permite explicar cada fila. Es álgebra lineal aplicada a una decisión de diseño.

### Apoyo visual

- Mostrar `docs/images/lienzo.png` y `docs/images/leyenda_mallas.png`.
- Dibujar en el tablero: `E − V + 1` y un ejemplo de dos ventanas.

### Transición

> Con las mallas ya tenemos `R · I = V`. Ahora veamos cómo se llena esa matriz automáticamente y cómo se resuelve. Eso lo explica mi compañero/a.

### Si hay poco tiempo

> Decir: “las ventanas son una base del espacio de ciclos; por eso la matriz es interpretable”.

---

## 4. Persona 4 — Del dibujo a la matriz: ensamblado, casos especiales y solución

**Tiempo:** 6:00 – 8:00
**Slides:** 7–8
**Objetivo:** explicar cómo se llena `R · I = V` automáticamente, qué casos especiales se resuelven y cómo se obtiene y verifica la solución.

### Guion

> Gracias. Yo explico cómo la aplicación llena la matriz automáticamente y cómo la resuelve.
>
> El usuario no escribe ninguna ecuación. El programa recorre cada malla detectada y, para cada componente, decide qué aporta. Si es una resistencia, suma su valor a la diagonal de esa malla. Si es una fuente, agrega su voltaje al vector `V` con el signo que corresponde según cómo la recorre el sentido horario. Después busca las resistencias que aparecen en dos mallas: esas son las compartidas y van fuera de la diagonal, con signo negativo cuando las dos corrientes de malla las recorren en sentidos opuestos. Así se construyen `R` y `V` sin intervención manual.
>
> Hay tres casos especiales que el programa atiende antes de resolver. Primero, las resistencias en paralelo real, es decir, las que unen el mismo par de nodos: se colapsan en una equivalente con `1/Req = Σ 1/Ri`, se resuelve el circuito y luego se reparte la corriente, aprovechando que todas comparten la misma tensión: `Ii = V / Ri`. Segundo, los puentes: una rama que no pertenece a ninguna ventana no entra en la matriz, pero sí aparece en los resultados. Tercero, si el sistema queda singular, se lanza un error controlado en lugar de mostrar números sin sentido.
>
> Para resolver usamos `np.linalg.solve`, que aplica una factorización LU con pivoteo parcial. **No calculamos la inversa**: resolver el sistema es más estable y más eficiente que invertir la matriz. El resultado es el vector de corrientes de malla.
>
> De ese vector salen todos los resultados. La corriente de una rama compartida es la diferencia de las corrientes de las dos mallas; la caída de tensión es `R · I`; y la potencia es `V · I`. Con eso se llena la tabla por componente.
>
> ¿Cómo sabemos que está bien? Verificamos las leyes de Kirchhoff en los circuitos de prueba, comprobamos que la suma de caídas de cada malla coincida con sus fuentes y comparamos con soluciones calculadas a mano. Hoy son 79 pruebas automatizadas.

### Apoyo visual

- Mostrar `docs/images/matrices_mallas.png`: señalar la diagonal y los términos fuera de ella.
- Mostrar `docs/images/leyenda_mallas.png` y `docs/images/resultados.png` para conectar matriz, mallas y tabla.

### Transición

> Ya tenemos la matriz armada, resuelta y verificada. Ahora veamos la aplicación funcionando y qué resultados obtuvimos.

### Si hay poco tiempo

> Decir: “la diagonal suma las resistencias de cada malla, fuera de la diagonal van las compartidas con signo negativo, los paralelos se reducen y se reparten, y el sistema se resuelve con LU”.

---

## 5. Persona 5 — Demo, arquitectura, resultados y cierre

**Tiempo:** 8:00 – 10:00
**Slides:** 9–10
**Objetivo:** demostrar la app, resumir la arquitectura y cerrar con las conclusiones.

### Guion

> Gracias. Les muestro la aplicación en funcionamiento.
>
> [Abrir la app con el circuito de ejemplo.]
>
> Aquí está el lienzo. Con `R` agrego resistencias y con `E` una fuente. Con `T` roto un componente y con clic derecho marco la tierra. Al presionar **Resolver circuito**, la aplicación detecta los nodos, encuentra las ventanas y construye el sistema.
>
> En el panel inferior vemos las tres matrices: `R`, `I` y `V`. Las filas y columnas están rotuladas `M1`, `M2`, etc. Abajo aparece la solución. A la derecha, la leyenda “Mallas detectadas” indica qué componentes pertenecen a cada malla; si hay resistencias en paralelo, se anota su equivalente, por ejemplo `R2 || R3 = 250 Ω`. En la tabla vemos corriente, voltaje y potencia por componente.
>
> La arquitectura está separada en capas: la interfaz en PyQt6, los modelos de componentes, el núcleo de grafos y solvers, y el panel de matrices. Eso permitió probar la lógica sin depender de la interfaz. Hoy tenemos **79 pruebas automatizadas**, `ruff` limpio, auditoría de dependencias sin vulnerabilidades conocidas y un ejecutable de Windows probado, de aproximadamente 14 MB, con un ZIP de distribución de 74 MB.
>
> Para cerrar: este proyecto no solo resuelve circuitos. Muestra que **el álgebra lineal es el puente** entre un problema físico y una solución computacional. El circuito se convierte en vector y matriz; la geometría elige una base; el método numérico resuelve; y la interfaz hace visible lo que normalmente queda en el papel.
>
> Las limitaciones son claras: trabajamos solo con corriente directa, resistencias y fuentes de voltaje, con un máximo de 20 resistencias y 3 fuentes. No hay AC, capacitores, inductores ni fuentes controladas. Como trabajo futuro quedan los builds de macOS y Linux, la automatización con GitHub Actions y la firma digital del ejecutable.
>
> Muchas gracias. Quedamos atentos a sus preguntas.

### Demo paso a paso

1. Abrir la aplicación (`uv run calc-resis-agbl` o el ejecutable).
2. Agregar una fuente de 12 V, una resistencia de 1 kΩ, una de 2 kΩ y una de 3 kΩ.
3. Rotar con `T` y conectar con el imán o con **Modo cable**.
4. Marcar tierra con clic derecho.
5. Elegir **Análisis por Mallas** y presionar **Resolver circuito**.
6. Señalar `R =`, `I =`, `V =`, la línea de solución y la leyenda de mallas.
7. Cerrar con la tabla de resultados y el resumen de potencias.

### Plan B si la demo falla

- Usar `docs/images/UI.png`, `matrices_mallas.png`, `leyenda_mallas.png` y `resultados.png`.
- Decir: “La aplicación ya fue probada; estas son las capturas del mismo circuito”.

### Cierre

> “Gracias. Nuestra conclusión es que un circuito es, para la computadora, un sistema lineal; y nuestro trabajo fue hacer ese sistema visible, comprensible y resoluble.”

---

## 6. Preguntas frecuentes y respuestas breves

| Pregunta | Respuesta sugerida |
| :--- | :--- |
| ¿Por qué usar mallas y no corrientes de rama? | Porque hay menos incógnitas: una por ventana. Además, la corriente de malla satisface automáticamente la Ley de Corrientes de Kirchhoff. |
| ¿También resuelven por nodos? | El proyecto incluye esa variante como apoyo interno, pero nuestro desarrollo y esta exposición se centran en mallas, que es el método que construimos a partir de la geometría del dibujo. |
| ¿Por qué todas las mallas en sentido horario? | Es una convención de signos. Cualquier orientación consistente funciona; el horario hace que la matriz sea más fácil de leer y de comparar. |
| ¿Qué pasa si el circuito no es planar? | La detección geométrica de ventanas no aplica; el programa usa ciclos fundamentales como respaldo. |
| ¿Por qué no calcular la inversa de la matriz? | Porque resolver `R · I = V` con LU es más estable y eficiente que calcular `R⁻¹` y multiplicar. |
| ¿Cómo saben que la solución es correcta? | Con pruebas que verifican las leyes de Kirchhoff, comparan con soluciones calculadas a mano y cubren casos con paralelos y puentes. |
| ¿Qué pasa si la matriz es singular? | Se muestra un error: el circuito puede estar abierto, mal conectado o tener mallas degeneradas. |
| ¿Cómo se manejan las resistencias en paralelo? | Se reducen a una equivalente para mallar y luego se reparte la corriente; la leyenda anota `R2 || R3 = valor`. |
| ¿Cómo se numeran las mallas? | De abajo hacia arriba y de izquierda a derecha; si hay empate, primero la de menor área. |
| ¿Por qué no usan SymPy? | Porque el problema es numérico: no necesitamos expresiones simbólicas, sino resolver un sistema con valores reales. |
| ¿Cuál es la limitación principal? | Solo DC resistivo: sin AC, capacitores, inductores ni fuentes controladas. |
| ¿La aplicación usa inteligencia artificial? | No. Usa teoría de grafos, álgebra lineal y métodos numéricos deterministas. |
| ¿Qué pasa si el usuario dibuja mal el circuito? | La app valida nodos desconectados, falta de tierra, resistencias inválidas y sistemas singulares antes de mostrar resultados. |

---

## 7. Cómo estirar la exposición a 15 minutos

Si el tiempo lo permite, cada persona agrega aproximadamente 1 minuto:

| Persona | Idea opcional |
| :--- | :--- |
| Persona 1 | Explicar la diferencia entre un problema físico y su modelo lineal; mencionar el principio de superposición. |
| Persona 2 | Deducir las dos ecuaciones de malla paso a paso y hablar del determinante y del rango. |
| Persona 3 | Explicar con más detalle `E − V + 1`, los puentes y las ventanas anidadas; mostrar un ejemplo de grafo no planar. |
| Persona 4 | Explicar con más detalle el ensamblado de la matriz, el reparto de paralelos y un ejemplo de sistema singular. |
| Persona 5 | Mostrar la arquitectura con más detalle, el proceso de pruebas y el build con PyInstaller. |

> No agregar diapositivas nuevas: profundizar en las existentes.

---

## 8. Checklist de ensayo

- [ ] Asignar nombres reales a las cinco personas.
- [ ] Ensayar al menos dos veces con cronómetro: una a 10 minutos y otra a 12.
- [ ] Probar la demo en el equipo que se usará en la exposición.
- [ ] Tener las capturas de respaldo abiertas en otra ventana.
- [ ] Verificar proyector, resolución y tema oscuro.
- [ ] Cerrar notificaciones y aplicaciones que puedan interrumpir.
- [ ] Practicar las transiciones entre personas.
- [ ] Preparar una frase de cierre común.
- [ ] Llevar el manual y el PDF como respaldo.

---

## 9. Anexo: ejemplo resuelto para el tablero

Circuito de dos mallas:

- Malla 1: fuente `V1 = 12 V`, `R1 = 1 kΩ`, resistencia compartida `R2 = 2 kΩ`.
- Malla 2: `R2 = 2 kΩ` compartida, `R3 = 3 kΩ`.

Ecuaciones de malla:

```text
Malla 1:  12 − 1·I1 − 2·(I1 − I2) = 0
Malla 2:  −2·(I2 − I1) − 3·I2 = 0
```

Forma matricial en kΩ y mA:

```text
[ 3  -2 ] [ I1 ]   [ 12 ]
[ -2  5 ] [ I2 ] = [  0 ]
```

Solución:

```text
det(R) = 3·5 − (−2)·(−2) = 11
I1 = (12·5) / 11 = 5.4545 mA
I2 = (3·0 + 2·12) / 11 = 2.1818 mA
```

Comprobación:

```text
Corriente por R2 = I1 − I2 = 3.2727 mA
Caída en R1 = 1 kΩ · 5.4545 mA = 5.4545 V
Caída en R2 = 2 kΩ · 3.2727 mA = 6.5454 V
Suma en la malla 1 = 12 V  ✓
```

En la aplicación, los valores se muestran en ohmios y amperios; la estructura de la matriz es la misma.

---

## 10. Frases de transición para memorizar

- **Persona 1 → 2:** “Si el circuito es un sistema de ecuaciones, veamos cómo se construye la matriz.”
- **Persona 2 → 3:** “Ya tenemos `R · I = V`; ahora veamos de dónde salen las mallas.”
- **Persona 3 → 4:** “Con la base de mallas elegida, veamos cómo se llena la matriz y cómo se resuelve.”
- **Persona 4 → 5:** “Con el modelo y el método numérico claros, veamos la aplicación funcionando.”
- **Persona 5 → cierre:** “Un circuito es, para la computadora, un sistema lineal; nuestro trabajo fue hacerlo visible.”
