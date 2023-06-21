from dcel import *

import math

def calculate_angle_acb(a: tuple, b: tuple, c: tuple) -> float:
    '''
    Calculates the angle abc, where b is the middle point...
    '''

    return 0
    


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
        get_angle_type(v)
        

        


