from dcel import *

import numpy as np
from numpy.linalg import norm

def calculate_angle_acb(a: tuple, b: tuple, c: tuple) -> float:
    '''
    Calculates the angle abc, where b is the middle point...
    '''

    # Calculate vectors ba and bc and then calculate their dot product
    ba = np.array(b) - np.array(a)
    bc = np.array(b) - np.array(c)

    # Calculate theta using the formula cos^-1 of dot product / product of norms...
    # This has 2 solutions, therefore we need to check the sin too by the cross product.
    theta = np.rad2deg(np.arccos(np.clip(np.dot(ba, bc) / (norm(ba) * norm(bc)), -1, 1)))

    if np.cross(ba, -bc) < 0:
        theta = (360 - theta) % 360

    return theta
    

def get_angle_type(v: Vertex) -> str:

    v_prev = v.outgoing_edge.prev.origin
    v_next = v.outgoing_edge.twin.origin

    v0 = v_prev.coords
    v1 = v.coords
    v2 = v_next.coords

    if v0[0] == v1[0] and v1[0] == v2[0]:
        return "colinear"
    
    theta = calculate_angle_acb(v0, v1, v2)

    print('Prev:', v0)
    print('Current:', v1)
    print('Next:', v2)
    print('\nAngle theta:', theta)
    print()


    if theta < 180 and v.is_left_of(v_prev) and v.is_left_of(v_next):
        return "start"
    elif theta > 180 and v.is_left_of(v_prev) and v.is_left_of(v_next):
        return "split"
    elif theta < 180 and (not v.is_left_of(v_prev)) and (not v.is_left_of(v_next)):
        return "stop"
    elif theta > 180 and (not v.is_left_of(v_prev)) and (not v.is_left_of(v_next)):
        return "merge"
    else:
        return "regular"
    



def monotonize_simple_polygon(poly: DCEL) -> None:
    '''
    Splits the polygon into monotone polygons.
    '''

    # The algorithm used to create monotone polygons is a sweep line algorithm...

    # First sort the vertices of the polygon in O(nlogn)
    vertices = sorted(
        poly.vertices,
        key=lambda vertex: (vertex.coords[0], vertex.coords[1])
    )

    # Sweep line
    for v in vertices:
        vertex_type = get_angle_type(v)

        print("Type of vertex is:", vertex_type)
        

        


