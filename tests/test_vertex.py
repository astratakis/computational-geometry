import pytest

from compgeo.dcel import *

__author__ = "astratakis"
__copyright__ = "astratakis"
__license__ = "MIT"


def test_vertex_creation():

    v = Vertex((1, 2))

    assert v.x == 1 and v.y == 2
