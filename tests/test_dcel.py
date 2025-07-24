import pytest

from compgeo.dcel import *

__author__ = "astratakis"
__copyright__ = "astratakis"
__license__ = "MIT"


def test_vertex_creation():

    v = Vertex(x=1, y=2)

    assert v.x == 1 and v.y == 2
    assert v.__str__() == "(1, 2)"


def test_edge_creation():

    v = Vertex(1, 2)
    e = Edge(v)

    assert e.origin == v
