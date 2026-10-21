import numpy as np

from calc_resis_agbl.core.graph_builder import GraphBuilder
from calc_resis_agbl.models.componentes import CircuitoError, FuenteDC, Resistencia


class MeshSolver:
    """
    Análisis por MALLAS (Leyes de Kirchhoff de tensión).

    Construye el sistema R · I = V sobre las corrientes de malla y, a partir de
    él, deriva la corriente, caída de tensión y potencia disipada por componente.
    """

    def resolver(self, componentes: list[object]) -> dict:
        builder = GraphBuilder()
        builder.construir_grafo(componentes)
        mallas = builder.extraer_mallas(componentes)

        n_mallas = len(mallas)
        if n_mallas == 0:
            raise CircuitoError(
                "No se detectaron mallas independientes; revisa el circuito."
            )

        matriz_r = np.zeros((n_mallas, n_mallas), dtype=float)
        vector_v = np.zeros(n_mallas, dtype=float)

        # Mapa rama -> (malla, sentido +1/-1). Una resistencia puede compartirse.
        for k, malla in enumerate(mallas):
            firmas = set()
            for rama in malla["ramas"]:
                elem = rama["elemento"]
                firma = (id(elem), elem.id)
                if firma in firmas:
                    continue
                firmas.add(firma)
                if isinstance(elem, Resistencia):
                    matriz_r[k, k] += elem.valor_ohms
                elif isinstance(elem, FuenteDC):
                    vector_v[k] += self._aporte_fuente(elem, rama)

        # Términos fuera de la diagonal: resistencia compartida entre mallas.
        compartidas: dict[tuple[int, str], list[int]] = {}
        for k, malla in enumerate(mallas):
            vistos = set()
            for rama in malla["ramas"]:
                elem = rama["elemento"]
                firma = (id(elem), elem.id)
                if firma in vistos:
                    continue
                vistos.add(firma)
                compartidas.setdefault(firma, []).append(k)

        for firma, mallas_idx in compartidas.items():
            if len(mallas_idx) != 2:
                continue
            elem = next((c for c in componentes if c.id == firma[1]), None)
            if not isinstance(elem, Resistencia):
                continue
            k, j = mallas_idx
            # Convención de mallas: la resistencia compartida aparece con signo
            # positivo si ambas corrientes de malla la recorren en el mismo
            # sentido, y negativo si lo hacen en sentidos opuestos.
            signo = self._signo_relativo(mallas[k], mallas[j], elem)
            termino = elem.valor_ohms * signo
            matriz_r[k, j] = termino
            matriz_r[j, k] = termino

        try:
            vector_i = np.linalg.solve(matriz_r, vector_v)
        except np.linalg.LinAlgError as ex:
            raise CircuitoError(
                "El sistema de mallas es singular o está mal condicionado."
            ) from ex

        resultados = self._resultados_por_componente(mallas, vector_i, componentes)
        return {
            "metodo": "mallas",
            "matriz_r": matriz_r,
            "vector_v": vector_v,
            "vector_i": vector_i,
            "mallas": mallas,
            "componentes": resultados,
        }

    @staticmethod
    def _aporte_fuente(fuente: FuenteDC, rama: dict) -> float:
        """Aporte de la fuente al vector V según el sentido de recorrido de la malla.

        Convención de mallas: al atravesar la fuente del polo - al + se produce
        una subida de tensión (+V); del + al - una caída (-V).
        """
        if rama["origen"] == fuente.nodo_negativo and rama["destino"] == fuente.nodo_positivo:
            return fuente.valor_voltios
        return -fuente.valor_voltios

    @staticmethod
    def _signo_relativo(malla_k: dict, malla_j: dict, elem: Resistencia) -> int:
        """+1 si ambas mallas recorren la resistencia en el mismo sentido, -1 si opuesto."""
        def sentido(malla: dict) -> int:
            for rama in malla["ramas"]:
                if rama["elemento"].id != elem.id:
                    continue
                if rama["origen"] == elem.nodo_a and rama["destino"] == elem.nodo_b:
                    return 1
                if rama["origen"] == elem.nodo_b and rama["destino"] == elem.nodo_a:
                    return -1
            return 0

        sk, sj = sentido(malla_k), sentido(malla_j)
        if sk == 0 or sj == 0:
            return -1
        return 1 if sk == sj else -1

    def _resultados_por_componente(
        self, mallas: list[dict], vector_i: np.ndarray, componentes: list[object]
    ) -> list[dict]:
        """Calcula I, V y P por componente sumando los aportes de cada malla."""
        resultados = []
        for comp in componentes:
            corriente = 0.0
            for k, malla in enumerate(mallas):
                vistos = set()
                for rama in malla["ramas"]:
                    if rama["elemento"].id != comp.id or comp.id in vistos:
                        continue
                    vistos.add(comp.id)
                    if isinstance(comp, Resistencia):
                        if (
                            rama["origen"] == comp.nodo_a
                            and rama["destino"] == comp.nodo_b
                        ):
                            corriente += vector_i[k]
                        else:
                            corriente -= vector_i[k]
                    else:
                        if (
                            rama["origen"] == comp.nodo_positivo
                            and rama["destino"] == comp.nodo_negativo
                        ):
                            corriente += vector_i[k]
                        else:
                            corriente -= vector_i[k]

            if isinstance(comp, Resistencia):
                voltaje = corriente * comp.valor_ohms
                potencia = voltaje * corriente
            else:
                voltaje = float(comp.valor_voltios)
                potencia = voltaje * corriente
            resultados.append(
                {
                    "id": comp.id,
                    "tipo": comp.tipo,
                    "corriente": corriente,
                    "voltaje": voltaje,
                    "potencia": potencia,
                }
            )
        return resultados
