"""Pruebas de la demo de Union-Find.  Correr con:  pytest"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from union_find import UnionFind


def test_estado_inicial():
    uf = UnionFind(6)
    assert uf.padre == [0, 1, 2, 3, 4, 5]
    assert uf.conjuntos == 6


def test_demo_paso_a_paso():
    uf = UnionFind(6)
    assert uf.union(0, 1) and uf.padre == [0, 0, 2, 3, 4, 5]
    assert uf.union(2, 3) and uf.padre == [0, 0, 2, 2, 4, 5]
    assert uf.union(1, 3) and uf.padre == [0, 0, 0, 2, 4, 5]
    assert uf.rango == [2, 0, 1, 0, 0, 0]
    assert uf.conjuntos == 3


def test_conectados():
    uf = UnionFind(6)
    uf.union(0, 1); uf.union(2, 3); uf.union(1, 3)
    assert uf.conectados(0, 2)
    assert not uf.conectados(0, 5)


def test_compresion_de_caminos():
    uf = UnionFind(6)
    uf.union(0, 1); uf.union(2, 3); uf.union(1, 3)
    assert uf.padre[3] == 2          # antes: 3 está a dos saltos de la raíz
    uf.find(3)
    assert uf.padre[3] == 0          # después: apunta directo a la raíz


def test_union_detecta_ciclo():
    uf = UnionFind(6)
    uf.union(0, 1); uf.union(2, 3); uf.union(1, 3)
    assert uf.union(0, 2) is False   # misma raíz: cerraría un ciclo
    assert uf.conjuntos == 3         # y no cambia nada
