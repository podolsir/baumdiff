import sys

def descend(tree, path, tree_adapter = None, child_seq_func = None):
    """
    Return the node in the ``tree`` that is identified by the sequence of 0-based indices in ``path``.
    If the path is an empty sequence, return the ``tree`` itself.

    Path examples:

    * The empty path ``[]`` denotes the root node in any tree
    * The path ``[0, 1, 2]`` denotes the 3rd child (index 2) of the 2nd child (index 1) of the 1st child (index 0) of the root node. 

    The ``child_seq_func`` parameter must either be ``None`` or be a callable which takes a single parameter (the tree node)
    and returns a `sequence <https://docs.python.org/3/glossary.html#term-sequence>`_
    of all child nodes of that tree node.
    If ``None``, the default implementation which returns the node itself is used.
    """
    tree_adapter = tree_adapter or _DTA
    child_seq_func = child_seq_func or tree_adapter.child_sequence
    return _descend(tree, path, child_seq_func) # pragma: no branch

def _descend(tree, path, S):
    if len(path) == 0:
        return tree
    return _descend(S(tree)[path[0]], path[1:], S)

def print_tree(root, indent = 0, indent_step = 2, tree_adapter = None, child_seq_func = None, file = sys.stdout):
    tree_adapter = tree_adapter or _DTA
    print(tree_adapter)
    child_seq_func = child_seq_func or tree_adapter.child_sequence
    print("%s%s (%s)" % (indent * ' ', root.id, root.value), file = file)
    for i in child_seq_func(root):
        print_tree(i, indent + indent_step, indent_step, child_seq_func = child_seq_func, file = file)

class DefaultTreeAdapter:
    def get_value(self, node):
        return node.value
    def set_value(self, node, value):
        node.value = value
    def add_child(self, node, kid, index):
        return node.add(kid, index)
    def remove_child(self, node, index):
        return node.remove(index)
    def get_parent(self, node):
        return node.parent
    def child_sequence(self, node):
        return node
    def value_eq(self, left, right):
        return left == right
    def get_path(self, node):
        return node.path
    def get_index(self, node, kid):
        return node.index(kid)
    def get_id(self, node):
        return node.id
    def clone_node(self, node, with_children=True):
        return node.clone(with_children)

_DTA = DefaultTreeAdapter()
