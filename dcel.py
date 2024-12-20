from shapely.geometry import polygon
from shapely.geometry.polygon import Polygon
from itertools import pairwise

import matplotlib.pyplot as plt

class Vertex:

    def __init__(self, coords: tuple):
        self.coords = coords
        self.x = coords[0]
        self.y = coords[1]
        self.outgoing_edge = None

    def is_above_of(self, other):

        if self.y > other.y:
            return True
        if self.y == other.y and self.x < other.x:
            return True
        return False

    def __str__(self):
        return str(self.coords)
    
    def __repr__(self) -> str:
        return self.__str__()

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

    def __init__(self, origin: Vertex = None, interior_face: Face = None):
        self.origin = origin
        self.interior_face = interior_face
        self.twin = None
        self.next = None
        self.prev = None

    def __str__(self):
        return str(self.prev.origin + " --> " + self.origin + " --> " + self.next.origin)
    
    def __repr__(self) -> str:
        return self.__str__()

class Dcel:

    def __init__(self, polygon_data: Polygon):
        self.vertices = list()
        self.edges = list()
        self.faces = set()

        for coords in polygon.orient(polygon_data).exterior.coords[:-1]:
            self.vertices.append(Vertex(coords))

        for v_origin, v_des in pairwise(self.vertices):
            h1 = Edge(v_origin)
            h2 = Edge(v_des)
            h1.twin = h2
            h2.twin = h1
            v_origin.outgoing_edge = h1
            self.edges.append(h1)
            self.edges.append(h2)

        # Create half-edge connecting last vertex to the fist vertex (also create the twin)
        h1 = Edge(self.vertices[-1])
        h2 = Edge(self.vertices[0])
        h1.twin = h2
        h2.twin = h1
        self.vertices[-1].outgoing_edge = h1
        self.edges.append(h1)
        self.edges.append(h2)

        for h1, h2 in zip(self.edges[0::2], self.edges[1::2]):
            h1_next = h2.origin.outgoing_edge
            h2_prev = h1_next.twin

            h1.next = h1_next
            h1_next.prev = h1

            h2.prev = h2_prev
            h2_prev.next = h2

        # Step 4: Face assignment (2 faces)
        start_inner_Edge = self.edges[0]

        # Bounded face
        f = Face()
        f.boundary_edge = start_inner_Edge
        tmp_Edge = start_inner_Edge
        while True:
            tmp_Edge.interior_face = f
            tmp_Edge = tmp_Edge.next
            if tmp_Edge is start_inner_Edge:
                break
        self.faces.add(f)

    def __plot__(self) -> plt.Figure:

        figure = plt.figure()
        
        for face in self.faces:
            if face.boundary_edge is None:
                continue
            face_edges = face.get_surrounding_edges()

            x, y = zip(*[face_edges[0].origin.coords] + [face_edges[i].next.origin.coords for i in range(len(face_edges))])

            plt.plot(x, y, '-', color='b')

        return figure


    def insert_diagonal(self, v1: Vertex, v2: Vertex, removable_face: Face) -> Edge:
        
        h1 = self.find_Edge_bounding_face_from_origin(v1, removable_face)
        h2 = self.find_Edge_bounding_face_from_origin(v2, removable_face)

        e1 = Edge(v1)
        e2 = Edge(v2)
        e1.twin = e2
        e2.twin = e1
        self.edges.append(e1)
        self.edges.append(e2)

        e1.next = h2
        e1.prev = h1.prev
        e2.next = h1
        e2.prev = h2.prev

        # Step 2: Connect the Dcel to the new edges
        h1.prev.next = e1
        h1.prev = e2
        h2.prev.next = e2
        h2.prev = e1

        # Step 3: Remove the old face (which was split in two) and create the two new faces and link them.
        f1 = Face()
        f2 = Face()
        self.faces.add(f1)
        self.faces.add(f2)
        self.faces.remove(removable_face)

        f1.boundary_edge = e1
        f2.boundary_edge = e2

        tmp_Edge = e1
        while True:
            tmp_Edge.interior_face = f1
            tmp_Edge = tmp_Edge.next
            if tmp_Edge is e1:
                break

        tmp_Edge = e2
        while True:
            tmp_Edge.interior_face = f2
            tmp_Edge = tmp_Edge.next
            if tmp_Edge is e2:
                break

        return e1


    @staticmethod
    def find_all_vertices_bounding_face(f):
        """ Given a face f return all vertices around the face in a list """
        vertices = list()
        tmp_Edge = f.boundary_edge
        while True:
            vertices.append(tmp_Edge.origin)
            tmp_Edge = tmp_Edge.next
            if tmp_Edge is f.boundary_edge:
                break
        return vertices

    @staticmethod
    def find_Edge_bounding_face_from_origin(v, f):
        """ Given a vertex v and a face f return the half-edge that has as origin v and bounds f """
        Edge = v.outgoing_edge
        while Edge.interior_face is not f:
            Edge = Edge.prev.twin
        return Edge

    @staticmethod
    def find_edge_connecting_origin_dest(orig, dest):
        """ Given a vertex orig and a vertex dest find the half-edge from orig to dest """
        Edge = orig.outgoing_edge
        while Edge.twin.origin is not dest:
            Edge = Edge.prev.twin
        return Edge

    @staticmethod
    def find_common_face_for_diagonal(v1, v2):
        """ Given two vertices v1, v2 where we know for a fact that a diagonal v1v2 is valid, find distinct face
        that will be cute in half by the diagonal """

        # Step 1: Find all faces that have v1 in their perimeter
        v1_faces = set()

        # loop around all half-edges with origin v1 and store interior_faces
        Edge = v1.outgoing_edge
        while True:
            v1_faces.add(Edge.interior_face)
            Edge = Edge.prev.twin
            if Edge is v1.outgoing_edge:
                break

        # loop around all half-edges with origin v2 and if the interior_face is in v1_faces (and is not the unbounded
        # face) then return it. Remember: We know for a fact that this face exists and is distinct
        # (because the diagonal v1v2 is valid)
        Edge = v2.outgoing_edge
        while True:
            if Edge.interior_face in v1_faces and Edge.interior_face.boundary_edge is not None:
                return Edge.interior_face
            Edge = Edge.prev.twin
