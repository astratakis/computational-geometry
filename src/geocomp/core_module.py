"""
Documentation for module dcel
"""

__author__ = "astratakis"
__copyright__ = "astratakis"
__license__ = "MIT"


class Vertex:

    def __init__(self, x: float, y: float, incident_edge: "Edge" = None):
        self.x = x
        self.y = y
        self.incident_edge = incident_edge


class Face:

    def __init__(self, name: str = None):
        self.name = name

    def __str__(self) -> str:
        string = ""
        return string


class Edge:

    def __init__(
        self,
        origin: Vertex,
        twin: "Edge" = None,
        next: "Edge" = None,
        prev: "Edge" = None,
        face: Face = None,
    ):
        self.origin = origin
        self.twin = twin
        self.next = next
        self.prev = prev
        self.face = face
