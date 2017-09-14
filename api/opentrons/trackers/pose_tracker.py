import numpy as np
from opentrons.containers.placeable import WellSeries
from opentrons.pubsub_util.messages.movement import moved_msg
from opentrons.pubsub_util.topics import MOVEMENT
from opentrons.util.trace import MessageBroker


def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


class Node(object):
    def __init__(self, object, parent=None):
        self.value = object
        self.parent = parent
        self.children = []

    def __repr__(self, level=0):
        ret = "\t"*level+repr(self.value)+"\n"
        for child in self.children:
            ret += child.__repr__(level+1)
        return ret

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)


class Pose(object):
    def __init__(self, x, y, z):
        self._pose = np.identity(4)
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return repr(self._pose)

    def __eq__(self, other):
        return (self._pose == other._pose).all()

    def __mul__(self, other):
        return self._pose.dot(other)

    @property
    def x(self):
        return self._pose[0][3]

    @x.setter
    def x(self, val):
        self._pose[0][3] = val

    @property
    def y(self):
        return self._pose[1][3]

    @y.setter
    def y(self, val):
        self._pose[1][3] = val

    @property
    def z(self):
        return self._pose[2][3]

    @z.setter
    def z(self, val):
        self._pose[2][3] = val

    @property
    def position(self):
        return np.array([self.x, self.y, self.z])


class PoseTracker(object):
    def __init__(self, broker: MessageBroker):
        self._root_nodes = []
        self._pose_dict = {}
        self.broker = broker
        self.broker.subscribe(MOVEMENT, self._object_moved)

    def __getitem__(self, obj):
        try:
            return self._pose_dict[obj][0]
        except KeyError:
            if isinstance(obj, WellSeries):  # FIXME:(09/12) remove WellSeries
                return self._pose_dict[obj[0]][0]
            raise KeyError("Position not tracked: {}".format(obj))

    def __contains__(self, item):
        return item in self._pose_dict

    def __iter__(self):
        return iter(self._pose_dict)

    def __setitem__(self, obj, pose):
        if not isinstance(pose, Pose):
            raise TypeError("{} is not an instance of Pose".format(pose))
        self._pose_dict[obj] = (pose, self._pose_dict[obj][1])

    def __str__(self):
        tree_repr = ''
        for root in self._root_nodes:
            pos_context = '\n\n' + repr(root)
            tree_repr += pos_context
        return tree_repr

    def clear(self):
        self._root_nodes = []
        self._pose_dict = {}

    def get_objects_in_subtree(self, root):
        '''Returns a list of objects in a subtree using a DFS tree traversal'''
        return flatten([root, [self.get_objects_in_subtree(item)
                               for item in self.get_object_children(root)]])

    def max_z_in_subtree(self, root):
        return max([self[obj].z for obj in
                    self.get_objects_in_subtree(root)])

    def track_object(self, parent, obj, x, y, z):
        '''Adds an object to the dict of object positions'''
        pose = Pose(*(self[parent].position + [x, y, z]))
        node = Node(obj)
        self._pose_dict[parent][1].add_child(node)
        self._pose_dict[obj] = (pose, node)

    def create_root_object(self, obj, x, y, z):
        '''Create a root node in the position tree. Though this could be done
        in the track_object() function if no parent is passed, we require
        this to be explicit because creating a new mapping context should
        not be a default behavior'''
        pose = Pose(x, y, z)
        node = Node(obj)
        self._pose_dict[obj] = (pose, node)
        self._root_nodes.append(node)

    def get_object_children(self, obj):
        '''Returns a list of child objects'''
        node = self._pose_dict[obj][1]
        return [child.value for child in node.children]

    def _translate_object(self, obj_to_trans, x, y, z):
        '''Translates a single object'''
        new_x, new_y, new_z, _ = self[obj_to_trans] * [x, y, z, 1]
        self[obj_to_trans] = Pose(new_x, new_y, new_z)

    def translate_object(self, obj_to_trans, x, y, z):
        '''Translates an object and its descendants'''
        self._translate_object(obj_to_trans, x, y, z)
        [self.translate_object(child, x, y, z)
         for child in self.get_object_children(obj_to_trans)] # recursive

    def _object_moved(self, moved_msg: moved_msg):
        '''
        Calculates an object movement as diff between current position
        and previous - translates moved object and its descendants
        by this difference
        '''
        mover, *new_pos = moved_msg
        self.translate_object(mover, *(new_pos - self[mover].position))

    def relative_object_position(self, target_object, reference_object):
        return self[target_object].position - self[reference_object].position

