"""Kruskal sobre la red de 6 computadoras, usando el Union-Find de union_find.py.

Problema: conectar A..F con cable al menor costo total y sin ciclos.
"""
from union_find import UnionFind, NOMBRES, ID

# (costo, u, v) — los mismos 8 cables de las diapositivas
CABLES = [
    (1, "A", "B"), (2, "D", "F"), (3, "B", "D"), (4, "E", "F"),
    (5, "D", "E"), (6, "A", "C"), (7, "C", "E"), (8, "B", "C"),
]


def kruskal(n, aristas, verbose=False):
    uf = UnionFind(n)
    arbol, costo = [], 0
    for paso, (w, u, v) in enumerate(sorted(aristas), start=1):   # 1) ordenar por peso
        ru, rv = uf.find(ID[u]), uf.find(ID[v])
        acepta = uf.union(ID[u], ID[v])                             # 2) union decide
        if acepta:
            arbol.append((u, v, w))
            costo += w
        if verbose:
            decision = "acepta" if acepta else "rechaza (ciclo)"
            print(f"Paso {paso}  {u}-{v} ({w})  find({u})={NOMBRES[ru]}  find({v})={NOMBRES[rv]}  -> {decision}")
            print(f"   padre = [{', '.join(NOMBRES[p] for p in uf.padre)}]   "
                  f"árbol: {len(arbol)} de {n - 1}   costo = {costo}")
        if len(arbol) == n - 1:                                     # 3) ya hay V-1 aristas
            break
    return arbol, costo


if __name__ == "__main__":
    print("Cables ordenados:", ", ".join(f"{u}-{v}({w})" for w, u, v in sorted(CABLES)))
    arbol, costo = kruskal(6, CABLES, verbose=True)
    print("Árbol de expansión mínima:", ", ".join(f"{u}-{v}({w})" for u, v, w in arbol))
    print("Costo total:", costo)
