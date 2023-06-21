from dcel import *

class Node:
    
    def __init__(self, edge: Edge = None) -> None:
        self.left = None
        self.right = None
        self.element = edge

    def __str__(self) -> str:
        return str(self.element)
    
class BinarySearchTree:

    def __init__(self, node: Node = None) -> None:
        self.root = node
        self.size = 0

    def insert(self, edge: Edge, vertex: Vertex) -> bool:
        '''
        Insert into the Binary search tree 
        '''

        # If the tree is empty, initialize the root...
        if self.root is None:
            self.root = Node(edge)
            self.size = 1
            return True
        
        node = self.root

        while True:
            if self.sweep_line_intersection(edge, vertex) > self.sweep_line_intersection(node.element, vertex):
                # In this case we go right...
                if node.right is None:
                    node.right = Node(edge)
                    return True
                node = node.right
                pass
            elif self.sweep_line_intersection(edge, vertex) < self.sweep_line_intersection(node.element, vertex):
                # In this case we fo left...
                if node.left is None:
                    node.left = Node(edge)
                    return True
                node = node.left
            else:
                return False
            
    def minimum(self, node: Node) -> Node:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def delete_recursively(self, node: Node, edge: Edge, vertex: Vertex) -> Node:
        if node is None:
            return None

        if self.sweep_line_intersection(edge, vertex) > self.sweep_line_intersection(node.element, vertex):
            node.right = self.delete_recursively(node.right, edge, vertex)
        elif self.sweep_line_intersection(edge, vertex) < self.sweep_line_intersection(node.element, vertex):
            node.left = self.delete_recursively(node.left, edge, vertex)
        else:  
            if node.left is None:
                tmp = node.right
                node = None
                return tmp
            elif node.right is None:
                tmp = node.left
                node = None
                return tmp

            # Node with two children: Get the inorder successor (smallest in the right subtree)
            tmp = self.minimum(node.right)

            # Copy the inorder successor's content to this node
            node.element = tmp.element

            # Delete the inorder successor
            node.right = self.delete_recursively(node.right, tmp.element, vertex)

        return node

    def delete(self, edge: Edge, vertex: Vertex) -> bool:
        self.delete_recursively(self.root, edge, vertex)
        return True
    
    def search_recursively(self, node: Node, vertex: Vertex) -> Edge:
        if node is None:
            return None
        if vertex.x == self.sweep_line_intersection(node.element, vertex):
            return node.element
        elif vertex.x > self.sweep_line_intersection(node.element, vertex):

            possibly_better = self.search_recursively(node.right, vertex)

            if possibly_better is None:
                return node.element
            else:
                return possibly_better
            
        return self.search_recursively(node.left, vertex)

    def find_edge_left_of_vertex(self, vertex: Vertex) -> Edge:
        return self.search_recursively(self.root, vertex)
        

    def sweep_line_intersection(self, edge: Edge, vertex: Vertex) -> float:
        
        origin = edge.origin.coords
        destination = edge.twin.origin.coords

        if origin[0] == destination[0]:
            return origin[0]
        
        elif origin[1] == destination[1]:
            return max(origin[0], destination[0])
        
        return ((destination[0] - origin[0]) * (vertex.coords[1] - origin[1])) / (destination[1] - origin[1]) + origin[0]

        

