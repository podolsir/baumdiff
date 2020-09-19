from .treeaccess import descend, DefaultTreeAdapter

class InsertOp(object):
    type = 'INS'
    def __init__(self, parentPath, node, index):
        (self.node, self.parentPath, self.index) = (node, parentPath, index)
    def __repr__(self):
        return "Insert %s to %s at index %s" % (
            self.node, self.parentPath, self.index)

class DeleteOp(object):
    type = 'DEL'
    def __init__(self, path):
        self.path = path
    def __repr__(self):
        return "Delete %s" % (self.path)

class UpdateOp(object):
    type = 'UPD'
    def __init__(self, path, value):
        (self.path, self.value) = path, value
    def __repr__(self):
        return "Update value of %s to %s" % (
            self.path, self.value)

class MoveOp(object):
    type = 'MOV'
    def __init__(self, path, newParentPath, index):
        (self.path, self.newParentPath, self.index) = (path, newParentPath, index)
    def __repr__(self):
        return "Move %s to %s at index %s" % (
            self.path, self.newParentPath, self.index)

class _ExecutorBase(object):
    def __init__(self):
        pass

    def execute(self, script, tree):
        for op in script:
            if op.type == 'INS':
                self.handleInsert(op, tree)
            elif op.type == 'UPD':
                self.handleUpdate(op, tree)
            elif op.type == 'MOV':
                self.handleMove(op, tree)
            elif op.type == 'DEL':
                self.handleDelete(op, tree)
            else:
                raise ValueError("Unknown operation type " + op.type)

    def handleMove(self, op, tree): # pragma: no cover
        raise NotImplementedError

    def handleInsert(self, op, tree): # pragma: no cover
        raise NotImplementedError

    def handleUpdate(self, op, tree): # pragma: no cover
        raise NotImplementedError

    def handleDelete(self, op, tree): # pragma: no cover
        raise NotImplementedError
    
class DefaultExecutor(_ExecutorBase):
    def __init__(self, tree_adapter=None, parent_getter=None, child_seq_func=None, value_setter=None,
        child_add_func=None, child_remove_func=None):
        
        _ExecutorBase.__init__(self)
        tree_adapter = tree_adapter or DefaultTreeAdapter()
        self.value_setter = value_setter or tree_adapter.set_value
        self.parent_getter = parent_getter or tree_adapter.get_parent
        self.child_add_func = child_add_func or tree_adapter.add_child
        self.child_remove_func = child_remove_func or tree_adapter.remove_child
        self.child_seq_func = child_seq_func or tree_adapter.child_sequence
 
    def handleMove(self, op, tree):
        node = descend(tree, op.path, child_seq_func =  self.child_seq_func)
        oldParent = self.parent_getter(node)
        newParent = descend(tree, op.newParentPath, child_seq_func = self.child_seq_func)
        self.child_remove_func(self.parent_getter(node), op.path[-1])
        newPos = op.index
        if oldParent == newParent and op.index >= op.path[-1]:
            newPos -= 1
        self.child_add_func(newParent, node, newPos)

    def handleInsert(self, op, tree):
        parent = descend(tree, op.parentPath, child_seq_func = self.child_seq_func)
        self.child_add_func(parent, op.node, op.index)

    def handleUpdate(self, op, tree):
        node = descend(tree, op.path, child_seq_func = self.child_seq_func)
        self.value_setter(node, op.value)

    def handleDelete(self, op, tree):
        parent = descend(tree, op.path[0:-1], child_seq_func = self.child_seq_func)
        self.child_remove_func(parent, op.path[-1])
