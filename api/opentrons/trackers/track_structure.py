''' This established a tree that tracks relationships
 between objects in the robot's world. This is meant to be SPARSE and
 is particularly focused on the following questions

 Question 1: If I move change the position of an object, what other objects should be adjusted?

 Answer 1: All children are understood to be positionally dependent on their parent. For example,
 if a container moves so should it's dependents (probably wells)

 Question 2: Can I get the position between any two objects?

 Answer 2: Any two objects that are in the same tree should be positionally connected

 '''


class Node(object):
    def __init__(self, object):
        children = []
        parent = None
        id = id(object)

    def add_child(self, object):
        new_node = Node(object)
        new_node.parent = self
        self.children.append(new_node)
