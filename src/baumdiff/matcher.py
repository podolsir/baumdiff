from collections import defaultdict
from .treeaccess import DefaultTreeAdapter

class IdMatcher(object):
    def __init__(self, tree_adapter=None, id_getter=None):
        tree_adapter = tree_adapter or DefaultTreeAdapter()
        self.id_getter = id_getter or tree_adapter.get_id

    def get_matching(self, tree1, tree2):
        matching = {}
        byid1 = self.get_id_index(tree1)
        def update(level):
            newlevel = []
            for node2 in level:
                matching[node2] = byid1[self.id_getter(node2)]
                newlevel.extend(iter(node2))
            if len(newlevel) > 0:
                update(newlevel)
        update([tree2])
        return matching

    def get_id_index(self, tree):
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
