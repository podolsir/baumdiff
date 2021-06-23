import bisect
import itertools
from baumdiff.simpletree import Node

class ShadowNode(Node):
    def __init__(self, *args):
        self.initialized = False
        self.allchildren = []
        self._fixups = []
        super().__init__(*args)
        self.status = []
        self.initialized = True

    def _add_del_index(self, index):
        bisect.insort(self._fixups, index)

    def _get_fixed_up_index(self, index):
        return index + sum(1 for _ in itertools.takewhile(lambda x: x <= index, self._fixups))

    def add(self, t, index = -1, status = 'inserted'):
        if self.initialized and not isinstance(t, ShadowNode):
            t = ShadowNode.convert(t)
        super().add(t, index)
        if index == -1:
            self.allchildren.append(t)
        else:
            self.allchildren.insert(self._get_fixed_up_index(index), t)
        if self.initialized:
            t.status.append(status)
            for i in range(len(self._fixups)):
                if index < self._fixups[i]:
                    self._fixups[i] += 1

    def remove(self, index, status = 'deleted'):
        super().remove(index)
        self.allchildren[self._get_fixed_up_index(index)].status.append(status)
        self._add_del_index(index)

    def _get_value(self):
        return super()._get_value()
    def _set_value(self, value):
        super()._set_value(value)
        self.status.append('updated')
    value = property(_get_value, _set_value)

    def clone(self, withChildren=True):
        if withChildren:
            children = [x.clone() for x in self._children]
        else:
            children = ()
        c = ShadowNode(self.id, self.value, *children)
        return c

    def __repr__(self): # pragma: no cover
        return "%s [%s]" % (self.id, ", ".join(self.status))
    
    @classmethod
    def convert(cls, ordinary):
        children = [ShadowNode.convert(x) for x in ordinary.children]
        return ShadowNode(ordinary.id, ordinary.value, *children)
