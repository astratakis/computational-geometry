from dcel import *

class Node:
    def __init__(self, edge):
        self.left = None
        self.right = None
        self.edge = edge

class BinarySearchTree:

    def __init__(self, root: Node = None) -> None:
        self.root = root
        self.size = 0

    def insert(self, edge: Edge, vertex: Vertex) -> bool:
        
        if self.root is None:
            self.root = Node(edge)
            self.size = 1
            return True

        node = self.root

        while True:

            if self.x_intersection_coord(edge, vertex) > self.x_intersection_coord(node.edge, vertex):
                if node.right is None:
                    node.right = Node(edge)
                    break
                else:
                    node = node.right
            elif self.x_intersection_coord(edge, vertex) < self.x_intersection_coord(node.edge, vertex):
                if node.left is None:
                    node.left = Node(edge)
                    break
                else:
                    node = node.left
            else:
                return False
        
        self.size += 1

        return True


    def min_value_node(self, node: Node) -> Node:
        
        current = node
        while True:
            if current.left is None:
                break
            else:
                current = current.left
        return current
    
    def delete(self, edge: Edge, vertex: Vertex) -> None:
        self.root = self.delete_recursive(self.root, edge, vertex)

    def delete_recursive(self, node: Node, edge, vertex):

        if node is None:
            return node

        if self.x_intersection_coord(edge, vertex) > self.x_intersection_coord(node.edge, vertex):  # 'edge' lies to the right
            node.right = self.delete_recursive(node.right, edge, vertex)
        elif self.x_intersection_coord(edge, vertex) < self.x_intersection_coord(node.edge, vertex):  # 'edge' lies to the left
            node.left = self.delete_recursive(node.left, edge, vertex)
        else:  # This is the node to be deleted (because we are dealing with polygon half-edges)
            # Node with only one child or no child
            if node.left is None:
                tmp = node.right
                node = None
                return tmp
            elif node.right is None:
                tmp = node.left
                node = None
                return tmp

            # Node with two children: Get the inorder successor (smallest in the right subtree)
            tmp = self.min_value_node(node.right)

            # Copy the inorder successor's content to this node
            node.edge = tmp.edge

            # Delete the inorder successor
            node.right = self.delete_recursive(node.right, tmp.edge, vertex)

        return node
    
    def find_edge_directly_to_the_left(self, vertex: Vertex) -> Edge:
        return self.find_edge_directly_to_the_left_recursive(self.root, vertex)


    def find_edge_directly_to_the_left_recursive(self, root, vertex):
        
        if root is None:
            return None
        if vertex.coords[0] == self.x_intersection_coord(root.edge, vertex):  # 'vertex' lies on this half-edge
            return root.edge
        elif vertex.coords[0] > self.x_intersection_coord(root.edge, vertex):
            tmp = self.find_edge_directly_to_the_left_recursive(root.right, vertex)  # Try to find closer half-edge
            if tmp is None:  # no closer half-edge
                return root.edge
            else:
                return tmp
        # Root's half-edge is to the right so try to find the half-edge from the left subtree
        return self.find_edge_directly_to_the_left_recursive(root.left, vertex)


    def x_intersection_coord(self, edge, vertex):
        """ Returns the x-coordinate of the intersection point between the parallel to x'x sweep line passing through
        vertex, with the edge. Important to note that we know for a fact that this intersection point exists and is
        to the left of the vertex.

        Keyword arguments:
        :param edge -- half-edge
        :param vertex -- Location of parallel to x'x sweep line (Sweep line intersects vertex at this point).
        :return: The x-coordinate of the intersection point between the parallel to x'x sweep line passing through
                :param vertex, with the :param edge
        """
        orig = edge.origin.coords
        dest = edge.twin.origin.coords
        if orig[0] == dest[0]:
            return orig[0]
        elif orig[1] == dest[1]:
            return max(orig[0], dest[0])  # segment parallel to x'x TODO: Think about this more
        return ((dest[0] - orig[0]) * (vertex.coords[1] - orig[1])) / (dest[1] - orig[1]) + orig[0]


