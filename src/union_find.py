"""Union-Find (conjuntos disjuntos) con unión por rango y compresión de caminos."""


class UnionFind:
    def __init__(self, n):
        self.padre = list(range(n))   # cada elemento es su propio conjunto
        self.rango = [0] * n
        self.conjuntos = n

    def find(self, x):
        """Devuelve la raíz del conjunto, con compresión de caminos."""
        if self.padre[x] != x:
            self.padre[x] = self.find(self.padre[x])
        return self.padre[x]

    def union(self, a, b):
        """Une dos conjuntos por rango. Devuelve False si ya estaban unidos."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rango[ra] < self.rango[rb]:
            ra, rb = rb, ra
        self.padre[rb] = ra
        if self.rango[ra] == self.rango[rb]:
            self.rango[ra] += 1
        self.conjuntos -= 1
        return True

    def conectados(self, a, b):
        return self.find(a) == self.find(b)

    def __repr__(self):
        return str(self.padre)


if __name__ == "__main__":
    uf = UnionFind(6)
    print(f"Inicial:        {uf}  conjuntos={uf.conjuntos}")

    uf.union(0, 1); print(f"union(0,1):     {uf}  conjuntos={uf.conjuntos}")
    uf.union(2, 3); print(f"union(2,3):     {uf}  conjuntos={uf.conjuntos}")
    uf.union(1, 3); print(f"union(1,3):     {uf}  conjuntos={uf.conjuntos}")

    print("¿0 y 2 conectados?", uf.conectados(0, 2))  # True
    print("¿0 y 5 conectados?", uf.conectados(0, 5))  # False

    uf.find(3)  # compresión de caminos: 3 pasa a apuntar directo a la raíz
    print(f"find(3):        {uf}  conjuntos={uf.conjuntos}")

    print("union(0,2) ->", uf.union(0, 2))            # False: ya estaban unidos (ciclo)
