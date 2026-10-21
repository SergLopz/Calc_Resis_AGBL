import numpy as np

from calc_resis_agbl.models.componentes import (
    NODO_REFERENCIA,
    CircuitoError,
    FuenteDC,
    Resistencia,
)


class NodalSolver:
    """
    Análisis NODAL por MNA (Modified Nodal Analysis), solo DC resistivo.

    Adaptado de la lógica validada del programa del docente, restringido a
    resistencias y fuentes de voltaje DC. El nodo de referencia (0) no es
    incógnita. Devuelve el mismo formato de resultados que MeshSolver.
    """

    def resolver(self, componentes: list[object]) -> dict:
        resistencias = [c for c in componentes if isinstance(c, Resistencia)]
        fuentes = [c for c in componentes if isinstance(c, FuenteDC)]

        nodos = set()
        for c in componentes:
            if isinstance(c, Resistencia):
                nodos.update((c.nodo_a, c.nodo_b))
            else:
                nodos.update((c.nodo_positivo, c.nodo_negativo))
        if NODO_REFERENCIA not in nodos:
            raise CircuitoError(
                f"Incluye el nodo de referencia '{NODO_REFERENCIA}' (tierra)."
            )

        names = sorted(n for n in nodos if n != NODO_REFERENCIA)
        idx = {n: i for i, n in enumerate(names)}
        n = len(names)
        m = len(fuentes)
        dim = n + m

        if dim == 0:
            raise CircuitoError("No hay variables para resolver.")

        a = np.zeros((dim, dim), dtype=float)
        rhs = np.zeros(dim, dtype=float)

        def at(nodo: str) -> int | None:
            return idx.get(nodo)

        # Contribución de resistencias (conductancias) por nodo.
        for r in resistencias:
            y = 1.0 / r.valor_ohms
            ia, ib = at(r.nodo_a), at(r.nodo_b)
            if ia is not None:
                a[ia, ia] += y
            if ib is not None:
                a[ib, ib] += y
            if ia is not None and ib is not None:
                a[ia, ib] -= y
                a[ib, ia] -= y

        # Ramas de fuente de voltaje (corriente incógnita + ecuación de lazo).
        for j, f in enumerate(fuentes):
            k = n + j
            for nodo, sgn in ((f.nodo_positivo, 1), (f.nodo_negativo, -1)):
                i = at(nodo)
                if i is not None:
                    a[i, k] += sgn
                    a[k, i] += sgn
            rhs[k] = f.valor_voltios

        # Guardar los índices de las corrientes de fuente para recuperarlas.
        voltajes_branch = {n + j: f for j, f in enumerate(fuentes)}

        try:
            sol = np.linalg.solve(a, rhs)
        except np.linalg.LinAlgError as ex:
            raise CircuitoError(
                "Sistema nodal singular: revisa nodos flotantes o fuentes incompatibles."
            ) from ex

        voltajes = {NODO_REFERENCIA: 0.0, **{name: sol[i] for name, i in idx.items()}}

        resultados = []
        for c in componentes:
            if isinstance(c, Resistencia):
                va, vb = voltajes[c.nodo_a], voltajes[c.nodo_b]
                voltaje = va - vb
                corriente = voltaje / c.valor_ohms
                potencia = voltaje * corriente
            else:
                va, vb = voltajes[c.nodo_positivo], voltajes[c.nodo_negativo]
                voltaje = va - vb
                k = next(
                    (k for k, f in voltajes_branch.items() if f.id == c.id), None
                )
                # Corriente por la fuente: incógnita MNA (de + hacia -).
                corriente = float(sol[k]) if k is not None else 0.0
                potencia = voltaje * corriente
            resultados.append(
                {
                    "id": c.id,
                    "tipo": c.tipo,
                    "corriente": corriente,
                    "voltaje": voltaje,
                    "potencia": potencia,
                }
            )

        return {
            "metodo": "nodal",
            "matriz_a": a,
            "vector_b": rhs,
            "solucion": sol,
            "nodos": voltajes,
            "componentes": resultados,
        }
