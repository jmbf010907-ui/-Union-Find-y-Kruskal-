import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from union_find import UnionFind, ID
from kruskal import kruskal, CABLES


def test_inicio():
    uf = UnionFind(6)
    assert uf.padre == [0, 1, 2, 3, 4, 5]
    assert uf.conjuntos == 6


def test_union_por_rango():
    uf = UnionFind(6)
    uf.union(ID["A"], ID["B"]); uf.union(ID["D"], ID["F"]); uf.union(ID["B"], ID["D"])
    assert uf.padre[ID["D"]] == ID["A"]          # rangos iguales: D cuelga de A
    assert uf.rango[ID["A"]] == 2
    assert uf.conjuntos == 3


def test_compresion():
    uf = UnionFind(6)
    uf.union(ID["A"], ID["B"]); uf.union(ID["D"], ID["F"]); uf.union(ID["B"], ID["D"])
    assert uf.padre[ID["F"]] == ID["D"]          # F está a dos saltos de A
    uf.union(ID["E"], ID["F"])                   # el cable E-F llama a find(F)
    assert uf.padre[ID["F"]] == ID["A"]          # después del find, apunta directo


def test_conectados_y_ciclo():
    uf = UnionFind(6)
    for u, v in [("A", "B"), ("D", "F"), ("B", "D"), ("E", "F")]:
        uf.union(ID[u], ID[v])
    assert uf.conectados(ID["B"], ID["E"])
    assert not uf.conectados(ID["A"], ID["C"])
    assert uf.union(ID["D"], ID["E"]) is False   # el cable D-E cerraría un ciclo


def test_kruskal():
    arbol, costo = kruskal(6, CABLES)
    assert costo == 16
    assert [(u, v) for u, v, _ in arbol] == [("A", "B"), ("D", "F"), ("B", "D"), ("E", "F"), ("A", "C")]
