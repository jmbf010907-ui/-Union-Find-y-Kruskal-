"""Union-Find (Disjoint Set Union) con unión por rango y compresión de caminos.

Problema de la exposición: 6 computadoras (A..F). Union-Find responde
"¿estas dos computadoras ya están conectadas?" sin recorrer la red.
"""


class UnionFind:
    def __init__(self, n):
        self.padre = list(range(n))   # cada uno es su propio conjunto
        self.rango = [0] * n          # cota de la altura de cada árbol
        self.conjuntos = n

    def find(self, x):
        if self.padre[x] != x:
            self.padre[x] = self.find(self.padre[x])   # compresión de caminos
        return self.padre[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                  # ya estaban unidos: sería un ciclo
        if self.rango[ra] < self.rango[rb]:
            ra, rb = rb, ra               # ra es el árbol más alto
        self.padre[rb] = ra
        if self.rango[ra] == self.rango[rb]:
            self.rango[ra] += 1
        self.conjuntos -= 1
        return True

    def conectados(self, a, b):
        return self.find(a) == self.find(b)


# ---- utilidades para trabajar con letras ----
NOMBRES = "ABCDEF"
ID = {c: i for i, c in enumerate(NOMBRES)}


def estado(uf):
    padre = ", ".join(NOMBRES[p] for p in uf.padre)
    rango = ", ".join(str(r) for r in uf.rango)
    return f"   padre = [{padre}]   rango = [{rango}]   conjuntos = {uf.conjuntos}"


def demo():
    """Instala los primeros cables de la red de 6 computadoras, uno por uno."""
    uf = UnionFind(6)
    print("Paso 0  UnionFind(6)   ningún cable instalado")
    print(estado(uf))

    print("Paso 1  cable A-B (1)   union(A, B) ->", uf.union(ID["A"], ID["B"]))
    print(estado(uf))
    print("Paso 2  cable D-F (2)   union(D, F) ->", uf.union(ID["D"], ID["F"]))
    print(estado(uf))
    print("Paso 3  cable B-D (3)   union(B, D) ->", uf.union(ID["B"], ID["D"]))
    print(estado(uf))
    print("Paso 4  cable E-F (4)   union(E, F) ->", uf.union(ID["E"], ID["F"]),
          "  (find(F): F -> D -> A y comprime)")
    print(estado(uf))
    print("Paso 5  ¿ya están conectadas?")
    print("        conectados(B, E) ->", uf.conectados(ID["B"], ID["E"]))
    print("        conectados(A, C) ->", uf.conectados(ID["A"], ID["C"]))
    print("Paso 6  cable D-E (5)   union(D, E) ->", uf.union(ID["D"], ID["E"]),
          "  (misma raíz: sería un ciclo)")
    print(estado(uf))
    return uf


if __name__ == "__main__":
    demo()
