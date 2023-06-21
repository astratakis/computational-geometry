import matplotlib.pyplot as plt

class Vertex():
    '''
    Implements a normal vertex (or node) in Eucledian 2D Space
    '''

    def __init__(self, coords: tuple) -> None:
        self.x = coords[0]
        self.y = coords[1]
        self.coords = coords
        self.outgoing_edge = None

    def __str__(self) -> str:
        return str(self.coords)
    
class Edge():
    '''
    Implements an edge between 2 vertices. In this context an edge is a half edge.
    Meaning that it contains pointers to it's twin edge
    '''

    def __init__(self, origin: Vertex) -> None:
        self.origin = origin        # It's origin point
        self.twin = None            # It's twin edge (Basically an edge that ends in origin and starts from the destination of this edge)
        self.face = None            # It's bounded face
        self.next = None            # It's clockwise/counterclockwise next
        self.prev = None            # Self explanatory...

    def __str__(self) -> str:
        prev_origin = "None" if self.prev is None else str(self.prev.origin)
        next_origin = "None" if self.next is None else str(self.next.origin)
        return "Prev: " + prev_origin + " --> " + str(self.origin) + " --> " + next_origin

class Face():

    '''
    The face of the polygon. This is also used to distinct the sub-polygons inside the DCEL data structure.
    Each face points to a bounded edge. If you follow a clockwise rotation among the edges of this face, it is guaranteed that you will
    return back to the initial edge.
    '''

    def __init__(self, bounded_edge: Edge = None) -> None:
        self.bounded_edge = bounded_edge

    # This function gets all the vertices that surround this face. The result is return as a list.
    def get_vertices(self) -> list:
        vertices = list()

        vertices.append(self.bounded_edge.origin)

        origin_vertex = self.bounded_edge.origin
        self.bounded_edge = self.bounded_edge.next

        while True:
            if self.bounded_edge.origin == origin_vertex:
                break
            else:
                vertices.append(self.bounded_edge.origin)
                self.bounded_edge = self.bounded_edge.next

        return vertices
    

    # This function returns all the edges that bound this face
    def get_edges(self) -> list:

        edges = list()

        edges.append(self.bounded_edge)

        initial_edge = self.bounded_edge
        self.bounded_edge = self.bounded_edge.next

        while True:
            if initial_edge == self.bounded_edge:
                break
            else:
                edges.append(self.bounded_edge)
                self.bounded_edge = self.bounded_edge.next

        return edges

class DCEL():

    def __init__(self, S = None) -> None:
        self.vertices = list()
        self.edges = list()
        self.faces = set()

        # This is equal to not inserting an existing set of points as an argument to the DCEL
        if S is None:
            return
        
        # Construct the DCEL from a simple polygon
        # CAUTION! This supposes that the input polygon is Simlpe.


        # Step 1: Create the list of vertices...
        for point in S:
            self.vertices.append(Vertex(point))

        # Step 2: Create edges in clockwise rotation...
        for i in range(len(self.vertices) - 1):

            # First get the origin and the destination of the inner edge.
            origin = self.vertices[i]
            destination = self.vertices[i+1]

            # Create an edge that starts from the origin and its twin that starts from the destination.
            e = Edge(origin)
            e.twin = Edge(destination)

            # Assign the newly created edge to the outgoing edge of the origin vertex.
            self.vertices[i].outgoing_edge = e

            self.edges.append(e)

        # Create references to the next pointers of the edges...
        for i in range(len(self.edges) - 1):
            self.edges[i].next = self.edges[i+1]
        self.edges[len(self.edges) - 1].next = self.edges[0]

        # Create references to the prev pointers of the edges...
        for i in range(1, len(self.edges)):
            self.edges[i].prev = self.edges[i-1]
        self.edges[0].prev = self.edges[len(self.edges) - 1]

        # Step 3: Create one Face, the face of the initial simple polygon
        face = Face(self.edges[0])

        # Add the face to the set.
        self.faces.add(face)

        # Finally dont forget to assign to all the edges that were created reference to the generated face i.e. the simple polygon
        for i in range(len(self.edges)):
            self.edges[i].face = face

    def __plot__(self) -> None:

        plt.figure()
        x, y = zip(*[self.edges[0].origin.coords] + [self.edges[i].next.origin.coords for i in range(len(self.edges))])
        plt.plot(x, y, '-')
        plt.title('DCEL')
        plt.show()
        