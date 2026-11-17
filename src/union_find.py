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
    uf = UnionFind(6)
    print("Paso 0  UnionFind(6)")
    print(estado(uf))

    print("Paso 1  union(A, B) ->", uf.union(ID["A"], ID["B"]))
    print(estado(uf))
    print("Paso 2  union(D, F) ->", uf.union(ID["D"], ID["F"]))
    print(estado(uf))
    print("Paso 3  union(B, D) ->", uf.union(ID["B"], ID["D"]))
    print(estado(uf))
    print("Paso 4  find(F) ->", NOMBRES[uf.find(ID["F"])], "  (compresión: F ahora apunta directo a A)")
    print(estado(uf))
    print("Paso 5  conectados(B, F) ->", uf.conectados(ID["B"], ID["F"]))
    print("        conectados(A, E) ->", uf.conectados(ID["A"], ID["E"]))
    print("Paso 6  union(B, F) ->", uf.union(ID["B"], ID["F"]), "  (misma raíz: sería un ciclo)")
    print(estado(uf))
    return uf


if __name__ == "__main__":
    demo()
