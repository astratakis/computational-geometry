from dcel import *
from bst import insert, delete, find_edge_directly_to_the_left
import numpy as np
from numpy.linalg import norm
from numpy import arccos, clip, dot, array, cross, rad2deg

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

def monotonize(polygon: Dcel) -> None:
    
    # (This BST along with the 'helper' dictionary form the status of the sweep line algorithm)
    root = None

    assignment = {}
    helper = {}

    # Sort the vertices on y-coordinate before the sweep. If two vertices have the same y-coordinate then
    # the leftmost one has higher priority. Thus, we first sort on ascending order for x-coordinate (secondary key),
    # and then sort on descending order for y-coordinate (primary key)
    vertices = sorted(
        sorted(polygon.vertices, key=lambda vertex: vertex.coords[0]),
        key=lambda vertex: vertex.coords[1],
        reverse=True
    )

    assign_type_to_vertices(polygon, assignment)


    for i, v_i in enumerate(vertices):
        print(f'Current value: {i}', end='\r')
        match assignment[v_i]:
            case "start vertex":
                
                e_i = v_i.outgoing_edge
                root = insert(root, e_i, v_i)
                helper[e_i] = v_i
            
            case "split vertex":
                
                e_i = v_i.outgoing_edge
                e_j = find_edge_directly_to_the_left(root, v_i)

                polygon.insert_diagonal(v_i, helper[e_j], e_j.interior_face)

                helper[e_j] = v_i
                root = insert(root, e_i, v_i)
                helper[e_i] = v_i

            case "end vertex":

                e_i_minus_1 = v_i.outgoing_edge.twin.next.twin

                if assignment[helper[e_i_minus_1]] == "merge vertex":
                    polygon.insert_diagonal(v_i, helper[e_i_minus_1], e_i_minus_1.interior_face)
                root = delete(root, e_i_minus_1, v_i)

            case "merge vertex":
                
                e_i_minus_1 = v_i.outgoing_edge.twin.next.twin  # e_(i-1)

                if assignment[helper[e_i_minus_1]] == "merge vertex":  # if helper(e_(i-1)) is a merge vertex
                    # Then insert the diagonal connecting v_i to helper(e_(i-1)) in the DCEL (which splits e_(i-1).interior_face)
                    polygon.insert_diagonal(v_i, helper[e_i_minus_1], e_i_minus_1.interior_face)

                root = delete(root, e_i_minus_1, v_i)  # Delete e_(i-1) from BST when sweep line is at vertex v_i

                # Search in BST to find the edge e_j directly left of v_i
                e_j = find_edge_directly_to_the_left(root, v_i)

                if assignment[helper[e_j]] == "merge vertex":  # if helper(e_j) is a merge vertex
                    # Then insert the diagonal connecting v_i to helper(e_j) in the DCEL (which splits e_j.interior_face)
                    polygon.insert_diagonal(v_i, helper[e_j], e_j.interior_face)

                helper[e_j] = v_i  # Set helper(e_j) to v_i

            case "regular vertex":
                e_i = v_i.outgoing_edge  # e_i
                e_i_minus_1 = e_i.twin.next.twin  # e_(i-1)

                v_i_minus_1 = e_i_minus_1.origin  # v_(i-1)
                v_i_plus_1 = v_i.outgoing_edge.twin.origin  # v_(i+1)

                # TODO: think this through more
                # if the interior of the polygon lies to the right of v_i. We are dealing with a regular vertex, thus,
                # the interior of the polygon lies to the right of v_i only when v_(i-1) is above v_(i+1)
                if v_i_minus_1.is_above_of(v_i_plus_1):
                    if assignment[helper[e_i_minus_1]] == "merge vertex":  # if helper(e_(i-1)) is a merge vertex
                        # Then insert the diagonal connecting v_i to helper(e_(i-1)) in DCEL (which splits e_(i-1).interior_face)
                        polygon.insert_diagonal(v_i, helper[e_i_minus_1], e_i_minus_1.interior_face)
                    root = delete(root, e_i_minus_1, v_i)  # Remove e_(i-1) from BST when sweep line is at vertex v_i
                    root = insert(root, e_i, v_i)  # insert half-edge e_i to BST when sweep line is at vertex v_i
                    helper[e_i] = v_i
                else:
                    # Search in BST to find the edge e_j directly left of v_i
                    e_j = find_edge_directly_to_the_left(root, v_i)
                    if assignment[helper[e_j]] == "merge vertex":  # if helper(e_j) is a merge vertex
                        # Then insert the diagonal connecting v_i to helper(e_j) in the DCEL (which splits e_j.interior_face)
                        polygon.insert_diagonal(v_i, helper[e_j], e_j.interior_face)
                    helper[e_j] = v_i


def assign_type_to_vertices(d, vertex_type):
    """ Assign the type attribute to all dcel vertices.

    Keyword arguments:
    :param d : dcel
    :param vertex_type : dictionary with key: Vertex, Value: The type of vertex  (To be assigned)
    """
    start_inner_edge = d.edges[0]  # we know for a fact edges[0] is a half-edge bounding the interior face

    tmp_edge = start_inner_edge
    while True:
        # we are always assigning the type of v_b (the middle vertex)
        assign_type_to_vertex(vertex_type, tmp_edge.prev.origin, tmp_edge.origin, tmp_edge.next.origin)
        tmp_edge = tmp_edge.next
        if tmp_edge is start_inner_edge:
            break


def assign_type_to_vertex(vertex_type, v_a, v_b, v_c):

    """ Assign the type attribute to a dcel vertex. We assign type to v_b only.

    Keyword arguments:
    :param vertex_type: dictionary with key: Vertex, value: The type of vertex (To be assigned)
    :param v_a: Vertex before v_b
    :param v_b: Vertex after v_a and before v_c, that is to be assigned a type
    :param v_c: Vertex after v_b

    We distinguish 5 types of polygon vertices (1-4 'turn' vertices):
    1. "start vertex" : If its two neighbors lie below it and the interior angle is less than 180
    2. "split vertex" : If its two neighbors lie below it and the interior angle is greater than 180
    3. "end vertex" : If its two neighbors lie above it and the interior angle is less than 180
    4. "merge vertex" : If its two neighbors lie above it and the interior angle is greater than 180
    5. "regular vertex" : Not 'turn' vertices. (not any of the 1-4)
    """
    if (angle_between_points_ccw(v_a.coords, v_b.coords, v_c.coords) < 180
            and v_b.is_above_of(v_a) and v_b.is_above_of(v_c)):
        vertex_type[v_b] = "start vertex"
    elif (angle_between_points_ccw(v_a.coords, v_b.coords, v_c.coords) > 180
          and v_b.is_above_of(v_a) and v_b.is_above_of(v_c)):
        vertex_type[v_b] = "split vertex"
    elif (angle_between_points_ccw(v_a.coords, v_b.coords, v_c.coords) < 180
          and (not v_b.is_above_of(v_a)) and (not v_b.is_above_of(v_c))):
        vertex_type[v_b] = "end vertex"
    elif (angle_between_points_ccw(v_a.coords, v_b.coords, v_c.coords) > 180
          and (not v_b.is_above_of(v_a)) and (not v_b.is_above_of(v_c))):
        vertex_type[v_b] = "merge vertex"
    else:
        vertex_type[v_b] = "regular vertex"


def triangulate_monotone_polygon(d, f):
    """ Triangulates y-monotone polygon defined by a face in the dcel and stores it in the dcel.
    Page 57, Computational Geometry, third edition, Mark de Berg
    :param d: dcel storing the y-monotone polygon
    :param f: face of the y-monotone polygon (to be triangulated) stored in the dcel
    """

    # Sort the vertices on y-coordinate before the sweep. If two vertices have the same y-coordinate then
    # the leftmost one has higher priority. Thus, we first sort on increasing order for x-coordinate (secondary key),
    # and then sort on decreasing order for y-coordinate (primary key)
    vertices = sorted(
        sorted(d.find_all_vertices_bounding_face(f), key=lambda vertex: vertex.coords[0]),
        key=lambda vertex: vertex.coords[1],
        reverse=True
    )

    # left_chain , right_chain both contain the top/bottom vertices (vertices[0], vertices[-1])
    left_chain, right_chain = left_right_chains(f, vertices[0], vertices[-1])

    stack = [vertices[0], vertices[1]]

    for j, v_j in enumerate(vertices[2:-1], start=2):

        # v_j in left_chain and vertex at the top of stack at right_chain. They lie on different chains
        if v_j in left_chain and stack[-1] in right_chain:
            # based on the geometry of the funnel in this case: bottom of stack is connected to v_j and the face
            # in which a diagonal (might) be inserted is exactly the face that is bounded by the half-edge
            # connecting the bottom of the stack with v_j
            next_face_to_be_split = d.find_edge_connecting_origin_dest(stack[0], v_j).interior_face

            while stack:  # while stack is not empty
                u = stack.pop(-1)
                if stack:  # If stack not empty
                    # Insert diagonal connecting v_j to u. The diagonal splits the face next_face_to_be_split.
                    # insert_diagonal also returns the new inserted half-edge diagonal v_j to u , hence, based on the
                    # geometry of the funnel in this case, the interior_face of the returned half-edge is the new
                    # interior face of the funnel. (In the next diagonal insertion that is the face that will be split)
                    next_face_to_be_split = d.insert_diagonal(v_j, u, next_face_to_be_split).interior_face
            stack.append(vertices[j-1])  # push v_(j-1) onto the stack
            stack.append(v_j)  # push v_j onto the stack

        # v_j in right_chain and vertex at the top of stack at left_chain. They lie on different chains
        elif v_j in right_chain and stack[-1] in left_chain:
            # based on the geometry of the funnel in this case: bottom of stack is connected to v_j and the face
            # in which a diagonal (might) be inserted is exactly the face that is bounded by the half-edge
            # connecting v_j to the vertex at the bottom of the stack
            next_face_to_be_split = d.find_edge_connecting_origin_dest(v_j, stack[0]).interior_face

            while stack:  # while stack is not empty
                u = stack.pop(-1)
                if stack:  # If stack not empty
                    # Insert diagonal connecting v_j to u. The diagonal splits the face next_face_to_be_split.
                    # insert_diagonal also returns the new inserted half-edge diagonal v_j to u , hence, based on the
                    # geometry of the funnel in this case, the interior_face of the returned half-edge's twin is the new
                    # interior face of the funnel. (In the next diagonal insertion that is the face that will be split)
                    next_face_to_be_split = d.insert_diagonal(v_j, u, next_face_to_be_split).twin.interior_face
            stack.append(vertices[j - 1])  # push v_(j-1) onto the stack
            stack.append(v_j)  # push v_j onto the stack

        # v_j in right_chain and vertex at the top of stack in right_chain. They lie on the same chain. Also, when
        # this is true, v_j is already connected to the top of stack.
        elif v_j in right_chain and stack[-1] in right_chain:
            u = stack.pop(-1)

            # based on the geometry of the funnel in this case: v_j is connected to the top of stack (u vertex) and
            # the face in which a diagonal (might) be inserted is exactly the face that is bounded by the half-edge
            # connecting v_j to the vertex u
            next_face_to_be_split = d.find_edge_connecting_origin_dest(v_j, u).interior_face

            # while stack not empty and a diagonal from v_j to top of stack is inside the polygon.
            while stack and ccw(v_j.coords, u.coords, stack[-1].coords):
                u = stack.pop(-1)

                # Insert diagonal connecting v_j to u. The diagonal splits the face next_face_to_be_split.
                # insert_diagonal also returns the new inserted half-edge diagonal v_j to u , hence, based on the
                # geometry of the funnel in this case, the interior_face of the returned half-edge is the new
                # interior face of the funnel. (In the next diagonal insertion that is the face that will be split)
                next_face_to_be_split = d.insert_diagonal(v_j, u, next_face_to_be_split).interior_face
            stack.append(u)  # Push the last vertex that has been popped back onto the stack
            stack.append(v_j)  # push v_j onto the stack

        # v_j in left_chain and vertex at the top of stack in left_chain. They lie on the same chain.
        else:
            u = stack.pop(-1)

            # based on the geometry of the funnel in this case: v_j is connected to the top of stack (u vertex) and
            # the face in which a diagonal (might) be inserted is exactly the face that is bounded by the half-edge
            # connecting u (the vertex that was popped from the top of stack) to v_j
            next_face_to_be_split = d.find_edge_connecting_origin_dest(u, v_j).interior_face

            # while stack not empty and a diagonal from v_j to top of stack is inside the polygon
            while stack and not ccw(v_j.coords, u.coords, stack[-1].coords):
                u = stack.pop(-1)

                # Insert diagonal connecting v_j to u. The diagonal splits the face next_face_to_be_split.
                # insert_diagonal also returns the new inserted half-edge diagonal v_j to u , hence, based on the
                # geometry of the funnel in this case, the interior_face of the returned half-edge's twin is the new
                # interior face of the funnel. (In the next diagonal insertion that is the face that will be split)
                next_face_to_be_split = d.insert_diagonal(v_j, u, next_face_to_be_split).twin.interior_face
            stack.append(u)  # Push the last vertex that has been popped back onto the stack
            stack.append(v_j)  # push v_j onto the stack

    # Add diagonals from v_n (lowest y-coordinate vertex in vertices) to all stack vertices except the first
    # and the last one. Note that because we cannot be certain of the geometry of the last vertices in the stack
    # we cannot find the face that will be split by the diagonal very quickly (like above). This is why we use the
    # find_common_face_for_diagonal function which basically returns in a brute force way that distinct face given
    # only the two vertices. (Read the function comments for more info). The leftover stack vertices are VERY, VERY rare
    stack.pop(0)
    stack.pop(-1)
    v_n = vertices[-1]
    while stack:
        u = stack.pop(-1)
        d.insert_diagonal(v_n, u, d.find_common_face_for_diagonal(v_n, u))


def triangulate_polygon(polygon: Dcel):
    """ Triangulates a simple polygon

    Keyword arguments:
    :param poly: A simple polygon to be triangulated
    :return: the DCEL storing the triangulated polygon
    """
    monotonize(polygon)
    faces = polygon.faces.copy()  # because we are going to add faces
    for f in faces:
        if f.boundary_edge is not None:
            triangulate_monotone_polygon(polygon, f)
        else:
            raise ValueError('Not in this sample data set...')


def left_right_chains(f, top_v, bot_v):
    """ Given a face f of a y-monotone polygon and the vertices at the top/bottom of the left/right polygonal chains,
    return the left and right polygonal chains.

    Keyword arguments:
    :param f: the face f of the y-monotone polygon in the DCEL
    :param top_v: the vertex at the top of the left/right polygonal chains
    :param bot_v: the vertex at the bottom of the left/right polygonal chains
    :return: the left and right polygonal chains.
    """

    left_chain = {top_v, bot_v}  # set - left chain of the y-monotone polygon (including top/bot vertices)
    right_chain = {top_v, bot_v}  # set - right chain of the y-monotone polygon (including top/bot vertices)

    # Locate top half-edge (that is, the half-edge bounding the polygon with origin the top vertex)
    tmp_edge = f.boundary_edge
    while True:
        if tmp_edge.origin is top_v:  # Then top half-edge is tmp_edge
            top_h = tmp_edge
            break
        tmp_edge = tmp_edge.next

    tmp_edge = top_h  # start from next half-edge from top half-edge
    add_to_left_chain = True  # boolean that tells us whether we add to the left or right chain
    while True:  # Loop around face in ccw, first adding vertices of the left chain and then of the right chain
        if add_to_left_chain:
            left_chain.add(tmp_edge.origin)
        else:
            right_chain.add(tmp_edge.origin)
        tmp_edge = tmp_edge.next

        if tmp_edge.origin is bot_v:  # reached bottom vertex, so now we are at the right chain part
            add_to_left_chain = False
        if tmp_edge is top_h:
            break

    return left_chain, right_chain


def angle_between_points_ccw(a, b, c):
    """ Given points a,b,c return the angle (in degrees) abc in respect to ccw rotation.
    (In other words, slightly abusing correct terminology, we can think that we move from a to b to c and the angle
    abc this function returns is always the one to left of us!)

    Keyword arguments:
    :param a: coords of the form (x,y). Point before b.
    :param b: coords of the form (x,y). Point after a and before c.
    :param c: coords of the form (x,y). Point after a.
    :return: The angle (in degrees) abc in respect to ccw rotation.
    """
    ba = array(a) - array(b)  # vector from b to a
    bc = array(c) - array(b)  # vector from b to c
    if ccw(a, b, c):  # if abc is counter-clockwise then the angle is 0-179.99... and all is good
        # Note: Due to floating-point presicion dot() can return 1.0000000000000002 so we have to be safe
        return rad2deg(arccos(clip(dot(ba, bc) / (norm(ba) * norm(bc)), -1, 1)))
    # abc is not ccw, thus the angle is reflex. Notice we (mod 360) and that is because if points are collinear
    # we want 0 degrees and NOT 360 degrees.
    # Note: Due to floating-point presicion dot() can return 1.0000000000000002 so we have to be safe
    return (360 - rad2deg(arccos(clip(dot(ba, bc) / (norm(ba) * norm(bc)), -1, 1)))) % 360


def ccw(a, b, c):
    return cross(array(b) - array(a), array(c) - array(b)) > 0


def point_in_triangle(a, b, c, p):
    """ Checks whether a point lies in the given triangle

    :param a: First vertex of the triangle (tuple with x and y coordinate)
    :param b: Second vertex of the triangle (tuple with x and y coordinate)
    :param c: Third vertex of the triangle (tuple with x and y coordinate)
    :param p: The point to be checked (tuple with x any y coordinate)
    :return: True if the point lies in the triangle, False otherwise
    """
    a = array(a)
    b = array(b)
    c = array(c)
    p = array(p)

    ab = b - a
    bc = c - b
    ca = a - c

    ap = p - a
    bp = p - b
    cp = p - c

    ab_cross_ap = cross(ab, ap)
    bc_cross_bp = cross(bc, bp)
    ca_cross_cp = cross(ca, cp)

    # TODO: Deal with the case where point lies on the edge for shortest path algo

    if ab_cross_ap == 0:  # points a,b,p collinear. Check if point p lies on segment ab
        if (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])) and (min(a[1], b[1]) <= p[1] <= max(a[1], b[1])):
            return True
        return False

    if bc_cross_bp == 0:  # points b,c,p collinear. Check if point p lies on segment bc
        if (min(c[0], b[0]) <= p[0] <= max(c[0], b[0])) and (min(c[1], b[1]) <= p[1] <= max(c[1], b[1])):
            return True
        return False

    if ca_cross_cp == 0:  # points a,c,p collinear. Check if point p lies on segment bc
        if (min(c[0], a[0]) <= p[0] <= max(c[0], a[0])) and (min(c[1], a[1]) <= p[1] <= max(c[1], a[1])):
            return True
        return False

    if ((ab_cross_ap > 0 and bc_cross_bp > 0 and ca_cross_cp > 0) or
            (ab_cross_ap < 0 and bc_cross_bp < 0 and ca_cross_cp < 0)):
        return True
    return False


def triangle_face_contains_point(face, p):
    triangle_coords = []
    tmp_edge = face.boundary_edge
    while True:
        triangle_coords.append(tmp_edge.origin.coords)
        tmp_edge = tmp_edge.next
        if tmp_edge is face.boundary_edge:
            break
    return point_in_triangle(triangle_coords[0], triangle_coords[1], triangle_coords[2], p)


def find_triangle_face_containing_point(triangulated_dcel, p):
    """
    For a triangulated dcel find the face that the point lies in

    :param triangulated_dcel : a triangulated dcel
    :param p: point p
    :return: The face
    """
    for f in triangulated_dcel.faces:
        if f.boundary_edge is None:
            continue
        if triangle_face_contains_point(f, p):
            return f


