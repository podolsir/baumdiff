from baumdiff import treeaccess
from baumdiff.simpletree import Node as N
from io import StringIO

SN = lambda x: N(x, x)

def test_print_tree():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    buf = StringIO()
    treeaccess.print_tree(t, 0, 2, file = buf)
    assert buf.getvalue() == "R (R)\n  A1 (A1)\n  A2 (A2)\n  A3 (A3)\n"

def test_print_tree_no_indent():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    buf = StringIO()
    treeaccess.print_tree(t, 0, 0, file = buf)
    assert buf.getvalue() == "R (R)\nA1 (A1)\nA2 (A2)\nA3 (A3)\n"
