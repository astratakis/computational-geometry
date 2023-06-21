from dcel import *

def generate_monotone(polygon: DCEL) -> DCEL:
    '''
    Transforms a polygon into several monotone polygons.
    '''

def triangulate_monotone_polygon(result: DCEL, poly_face: Face) -> None:
    '''
    Triangulate a Y-monotone polygon.
    '''

    # Get the vertices that are the outer bound of the monotone polygon face.
    vertices = poly_face.get_vertices()

    # Initialize an empty queue with preallocated space to prepare for the merging of the chains...
    queue = [None] * len(vertices)

    # Get the upper point of the chains.
    upper = max(
        vertices,
        lambda x: x[1]
    )

    # Get the lower point of the chains.
    lower = min(
        vertices,
        lambda x: x[1]
    )

    # Create the chains

    left_chain = []
    right_chain = []

def triangulate_simple_polygon(polygon: DCEL) -> DCEL:
    '''
    Triangulates a simple polygon. It first splits the initial polygon into several monotone polygons.
    The 'splitting' does not create more DCELs, but the polygons are embeded into the initial DCEL as faces.
    '''

    # Step 1: Create monotone polygons.
    result = generate_monotone(polygon)

    # Step 2: Get all the faces of the monotone polygons that were creates. Notice that since the initial polygon is simple, it has only one face.
    monotone_faces = result.faces.copy()
    for face in monotone_faces:
        if face.bounded is not True:
            raise ValueError("Detected unbounded face in a simpmle polygon...")
        else:
            triangulate_monotone_polygon(result, face)
    
    return result
