from collections import defaultdict
from .treeaccess import DefaultTreeAdapter

class Node(object):
    def __init__(self, id, value, *args):
        self.id = id
        self._value = value
        self._parent = None
        self._children = []
        for i in args:
            self.add(i)

    def _get_value(self):
        return self._value
    def _set_value(self, value):
        self._value = value
    value = property(_get_value, _set_value)

    def _get_children(self):
        return self._children
    children = property(_get_children)

    def _get_parent(self):
        return self._parent
    parent = property(_get_parent)

    def __getitem__(self, index):
        return self.children[index]

    def __len__(self):
        return len(self.children)

    def __iter__(self):
        return iter(self.children)


    def index(self, kid):
        return self.children.index(kid)

    def _get_path(self):        
        if self.parent is None:
            return []
        pp = self.parent.path
        pp.append(self.parent.index(self))
        return pp

    path = property(_get_path)

    def add(self, t, index = -1):
        t._parent = self
        if index == -1:
            self._children.append(t)
        else:
            self._children.insert(index, t)

    def remove(self, index):
        t = self._children[index]
        t._parent = None
        del self._children[index]

    def __eq__(self, other):
        return other is not None and self.id == other.id
    def __ne__(self, other):
        return not(self == other)
    def __hash__(self):
        return hash(self.id)
    def __repr__(self):
        return self.id

    def clone(self, withChildren=True):
        if withChildren:
            children = [x.clone() for x in self._children]
        else:
            children = ()
        c = Node(self.id, self.value, *children)
        return c

class Matcher(object):
    def __init__(self, tree_adapter=None, id_getter=None):
        tree_adapter = tree_adapter or DefaultTreeAdapter()
        self.id_getter = id_getter or tree_adapter.get_id

    def getMatching(self, tree1, tree2):
        matching = {}
        byid1 = self.getIdIndex(tree1)
        def update(level):
            newlevel = []
            for node2 in level:
                matching[node2] = byid1[self.id_getter(node2)]
                newlevel.extend(iter(node2))
            if len(newlevel) > 0:
                update(newlevel)
        update([tree2])
        return matching

    def getIdIndex(self, tree):
        byid = defaultdict(lambda: None)
        def update(level):
            newlevel = []
            for node in level:
                byid[self.id_getter(node)] = node
                newlevel.extend(iter(node))
            if len(newlevel) > 0:
                update(newlevel)
        update([tree])
        return byid      
