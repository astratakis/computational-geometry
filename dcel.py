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
    
    def is_above_of(self, other) -> bool:
        
        if self.y > other.y:
            return True
        if self.y == other.y and self.x < other.x:
            return True
        return False
    
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
        return prev_origin + " --> " + str(self.origin) + " --> " + next_origin
    
    def __repr__(self) -> str:
        return self.__str__()

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
    
    def __plot__(self):
        plt.figure()

        edges = self.get_edges()

        x, y = zip(*[edges[0].origin.coords] + [edges[i].next.origin.coords for i in range(len(edges))])

        plt.plot(x, y, '-')
        plt.show()

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
        for point in S[:-1]:
            self.vertices.append(Vertex(point))

        # Step 2: Create edges in clockwise rotation...
        for i in range(len(self.vertices) - 1):

            # First get the origin and the destination of the inner edge.
            origin = self.vertices[i]
            destination = self.vertices[i+1]

            # Create an edge that starts from the origin and its twin that starts from the destination.
            e = Edge(origin)
            e.twin = Edge(destination)
            e.twin.twin = e

            # Assign the newly created edge to the outgoing edge of the origin vertex.
            self.vertices[i].outgoing_edge = e

            # Add the newly created edge to the list of edges...
            self.edges.append(e)
        
        # Dont forget to add the final edge. i.e. from the last vertex to the initial vertex
        final_edge = Edge(self.vertices[-1])
        final_edge.twin = Edge(self.vertices[0])
        final_edge.twin.twin = final_edge
        self.vertices[-1].outgoing_edge = final_edge
        self.edges.append(final_edge)

        # Create references to the next pointers of the edges...
        for i in range(len(self.edges) - 1):
            self.edges[i].next = self.edges[i+1]
        self.edges[len(self.edges) - 1].next = self.edges[0]

        # Create references to the prev pointers of the edges...
        for i in range(1, len(self.edges)):
            self.edges[i].prev = self.edges[i-1]
        self.edges[0].prev = self.edges[len(self.edges) - 1]

        # Create reference to twins...

        for i in range(len(self.edges)):
            self.edges[i].twin.next = self.edges[i].prev.twin
            self.edges[i].twin.prev = self.edges[i].next.twin
            self.edges[i].twin.origin = self.edges[i].next.origin

        # Step 3: Create one Face, the face of the initial simple polygon
        face = Face(self.edges[0])

        # Add the face to the set.
        self.faces.add(face)

        # Finally dont forget to assign to all the edges that were created reference to the generated face i.e. the simple polygon
        for i in range(len(self.edges)):
            self.edges[i].face = face

    def __plot__(self) -> None:
        
        all_edges = []
        for face in self.faces:
            face_edges = face.get_edges()

            for fage in face_edges:
                all_edges.append(fage)

        x, y = zip(*[all_edges[i].origin.coords for i in range(len(all_edges))])

        plt.figure()
        plt.plot(x, y, '-')
        plt.show()

    def insert_diagonal(self, v1: Vertex, v2: Vertex) -> None:
        print('Diagonal between:', v1, 'and', v2)

        # Prepare the new edge to add
        upper_vertex = None
        lower_vertex = None

        # Get the upper and lower vertices. Since the rotation of the inner vertices is counter clockwise, the diagonal should have origin the upper vertex.
        if v1.is_above_of(v2):
            upper_vertex = v1
            lower_vertex = v2
        else:
            upper_vertex = v2
            lower_vertex = v1

        diagonal = Edge(upper_vertex)
        diagonal.twin = Edge(lower_vertex)
        diagonal.twin.twin = diagonal

        upper_vertex.outgoing_edge.twin.next.twin.next = diagonal
        lower_vertex.outgoing_edge.twin.next.twin.next = diagonal.twin

        diagonal.next = lower_vertex.outgoing_edge
        diagonal.twin.next = upper_vertex.outgoing_edge

        diagonal.prev = upper_vertex.outgoing_edge.twin.next.twin
        diagonal.twin.prev = lower_vertex.outgoing_edge.twin.next.twin

        self.edges.append(diagonal)

        face1 = Face(diagonal)
        face2 = Face(diagonal.twin)

        diagonal.face = face1
        diagonal.twin.face = face2

        previous_face = upper_vertex.outgoing_edge.face
        self.faces.remove(previous_face)

        current = diagonal.next

        while True:
            if current == diagonal:
                break

            current.face = face1
            current = current.next

        current = diagonal.twin.next



        while True:
            if current == diagonal.twin:
                break

            current.face = face2
            current = current.next

        self.faces.add(face1)
        self.faces.add(face2)


        self.__plot__()
        

