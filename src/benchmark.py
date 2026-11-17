"""Mide el efecto de las optimizaciones de Union-Find.

Uso:  python benchmark.py
"""
import time, sys

class UF:
    """Union-Find configurable: se pueden apagar las optimizaciones."""
    def __init__(self, n, compresion=True, rango=True):
        self.padre = list(range(n))
        self.rango = [0] * n
        self.usar_compresion = compresion
        self.usar_rango = rango
        self.saltos = 0                      # cuenta el trabajo de find

    def find(self, x):
        raiz = x
        while self.padre[raiz] != raiz:      # versión iterativa: no revienta la pila
            raiz = self.padre[raiz]
            self.saltos += 1
        if self.usar_compresion:
            while self.padre[x] != raiz:
                siguiente = self.padre[x]
                self.padre[x] = raiz
                x = siguiente
        return raiz

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.usar_rango:
            if self.rango[ra] < self.rango[rb]:
                ra, rb = rb, ra
            self.padre[rb] = ra
            if self.rango[ra] == self.rango[rb]:
                self.rango[ra] += 1
        else:
            self.padre[ra] = rb              # cuelga sin mirar la altura: forma cadenas largas
        return True


def prueba(n, compresion, rango):
    """Peor caso para Union-Find: une 0-1, 1-2, 2-3 ... formando una cadena,
    y despues consulta find() de todos los elementos."""
    uf = UF(n, compresion, rango)
    t0 = time.perf_counter()
    for i in range(n - 1):
        uf.union(i, i + 1)
    for i in range(n):
        uf.find(i)
    return time.perf_counter() - t0, uf.saltos


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    print(f"n = {n} elementos\n")
    print(f"{'configuración':<34}{'saltos de padre':>18}{'tiempo (s)':>14}")
    print("-" * 66)
    for etiqueta, c, r in [
        ("sin optimizaciones",            False, False),
        ("solo compresión de caminos",    True,  False),
        ("solo unión por rango",          False, True),
        ("compresión + rango",            True,  True),
    ]:
        t, saltos = prueba(n, c, r)
        print(f"{etiqueta:<34}{saltos:>18,}{t:>14.4f}")
