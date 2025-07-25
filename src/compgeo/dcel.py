"""
Documentation for module dcel
"""

__author__ = "astratakis"
__copyright__ = "astratakis"
__license__ = "MIT"


class Vertex:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


class Face:

    def __init__(self):
        self.boundary_edge = None

    def __str__(self) -> str:
        return "Face"

    def __repr__(self) -> str:
        return self.__str__()

    def get_surrounding_edges(self) -> list:
        edges = list()

        initial = self.boundary_edge
        current = initial.next
        edges.append(initial)

        while True:
            if initial is current:
                break
            else:
                edges.append(current)
                current = current.next

        return edges


class Edge:

    def __init__(self, origin: Vertex, interior_face: Face = None):
        self.origin = origin
        self.interior_face = interior_face
        self.twin = None
        self.next = None
        self.prev = None

    def __str__(self):
        return str(
            self.prev.origin + " --> " + self.origin + " --> " + self.next.origin
        )
