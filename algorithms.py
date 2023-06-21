from dcel import *
from bst import *

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

    #print('Prev:', v0)
    #print('Current:', v1)
    #print('Next:', v2)
    #print('\nAngle theta:', theta)
    #print()

    if theta < 180 and v.is_above_of(v_prev) and v.is_above_of(v_next):
        return "start"
    elif theta > 180 and v.is_above_of(v_prev) and v.is_above_of(v_next):
        return "split"
    elif theta < 180 and (not v.is_above_of(v_prev)) and (not v.is_above_of(v_next)):
        return "stop"
    elif theta > 180 and (not v.is_above_of(v_prev)) and (not v.is_above_of(v_next)):
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
        sorted(
            poly.vertices,
            key=lambda vertex: vertex.coords[0],
            reverse=False
        ),
        key=lambda vertex: vertex.coords[1],
        reverse=True
    )

    types = [get_angle_type(v) for v in vertices]

    # Create a hashmap of attributes...
    # Key is the vertex and value is the type (start, stop, merge, split, regular...)
    attributes = {}
    for index, v in enumerate(vertices):
        attributes[v] = types[index]

    print(types)

    # Initialize a binary search tree
    tree = BinarySearchTree()

    # Initialize helper dictionary
    helper = {}

    for index, v in enumerate(vertices):

        print('Executing request:', types[index])
        
        match types[index]:
            case "start":
                
                e_current = v.outgoing_edge
                helper[e_current] = v
                tree.insert(e_current, v)

                pass
            case "stop":

                # Get the previous edge
                e_prev = v.outgoing_edge.twin.next.twin

                # If the helper vertex of the previous edge is merge, then create a diagonal that connects current vertex v, with the helper vertex of the previous edge...
                if attributes[helper[e_prev]] == "merge":
                    poly.insert_diagonal(v, helper[e_prev])

                # Then delete the edge from the tree
                tree.delete(e_prev, v)

                pass
            case "split":

                e_i = v.outgoing_edge
                e_j = tree.find_edge_left_of_vertex(v)

                poly.insert_diagonal(v, helper[e_j])

                helper[e_j] = v
                tree.insert(e_i, v)
                helper[e_i] = v

                pass
            case "merge":

                e_prev = v.outgoing_edge.twin.next.twin

                if attributes[helper[e_prev]] == "merge":
                    poly.insert_diagonal(v, helper[e_prev])
                
                tree.delete(e_prev, v)

                e_j = tree.find_edge_left_of_vertex(v)

                if attributes[helper[e_j]] == "merge":
                    poly.insert_diagonal(v, helper[e_j])
                
                helper[e_j] = v

                pass
            case "regular":

                e_i = v.outgoing_edge  # e_i
                e_i_minus_1 = e_i.twin.next.twin  # e_(i-1)

                v_i_minus_1 = e_i_minus_1.origin  # v_(i-1)
                v_i_plus_1 = v.outgoing_edge.twin.origin  # v_(i+1)

                if v_i_minus_1.is_above_of(v_i_plus_1):
                    if attributes[helper[e_i_minus_1]] == "merge":  # if helper(e_(i-1)) is a merge vertex
                        # Then insert the diagonal connecting v_i to helper(e_(i-1)) in DCEL (which splits e_(i-1).incident_face)
                        poly.insert_diagonal(v, helper[e_i_minus_1])
                    tree.delete(e_i_minus_1, v)  # Remove e_(i-1) from BST when sweep line is at vertex v_i
                    tree.insert(e_i, v)  # insert half-edge e_i to BST when sweep line is at vertex v_i
                    helper[e_i] = v
                else:
                    # Search in BST to find the edge e_j directly left of v_i
                    e_j = tree.find_edge_left_of_vertex(v)
                    if attributes[helper[e_j]] == "merge":  # if helper(e_j) is a merge vertex
                        # Then insert the diagonal connecting v_i to helper(e_j) in the DCEL (which splits e_j.incident_face)
                        poly.insert_diagonal(v, helper[e_j])
                    helper[e_j] = v

                pass
            case "colinear":
                # Inore the point if it is colinear with other points...
                pass
            