
class Vertex():
    '''
    Implements a normal vertex (or node) in Eucledian 2D Space
    '''

    def __init__(self, coords: tuple) -> None:
        self.x = coords[0]
        self.y = coords[1]
        self.outgoing_edge = None

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
        return str("Edge from vertex: " + str(self.origin))


class Face():

    '''
    The face of the polygon. This is also used to distinct the sub-polygons inside the DCEL data structure.
    Each face points to a bounded edge. If you follow a clockwise rotation among the edges of this face, it is guaranteed that you will
    return back to the initial edge.
    '''

    def __init__(self) -> None:
        self.bounded = False
        self.bounded_edge = None

    def get_vertices(self) -> list:
        return list()

class DCEL():

    def __init__(self, S = None) -> None:
        self.vertives = list()
        self.edges = list()
        self.faces = set()

        # This is equal to not inserting an existing set of points as an argument to the DCEL
        if S is None:
            return
        
        # Construct the DCEL from a simple polygon
        # CAUTION! This supposes that the input polygon is Simlpe.


        # Step 1: Create the list of vertices...

        print(S)
        



