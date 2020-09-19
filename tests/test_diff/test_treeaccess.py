from baumdiff import treeaccess
from baumdiff.simpletree import Node as N
from io import StringIO

SN = lambda x: N(x, x)

def test_print_tree():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    buf = StringIO()
    treeaccess.print_tree(t, 0, 2, file = buf)
    buf == "R\n  A1\n  A2\n  A3"

def test_print_tree_no_indent():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    buf = StringIO()
    treeaccess.print_tree(t, 0, 0, file = buf)
    buf == "R\nA1\nA2\nA3"
