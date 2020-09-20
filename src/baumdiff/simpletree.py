class Node(object):
    def __init__(self, id, value, *children):
        self.id = id
        self._value = value
        self._parent = None
        self._children = []
        for i in children:
            self.add(i)

    def _get_value(self):
        return self._value
    def _set_value(self, value):
        self._value = value
    value = property(_get_value, _set_value)

    @property
    def children(self):
        return self._children

    @property
    def parent(self):
        return self._parent

    def __getitem__(self, index):
        return self._children[index]

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return iter(self._children)

    def index(self, kid):
        return self._children.index(kid)

    @property
    def path(self):        
        if self.parent is None:
            return []
        pp = self.parent.path
        pp.append(self.parent.index(self))
        return pp

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
