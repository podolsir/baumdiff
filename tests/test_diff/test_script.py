import pytest
from collections import namedtuple
from baumdiff.simpletree import Node as N
from baumdiff import script

@pytest.mark.xfail
def test_unknown_op():
    t = N("R", "R")
    op = namedtuple("SomeOp", ["type"])(type="foo")
    ex = script.DefaultExecutor()
    ex.execute([op], t)

def test_repr():
    # It's enough if the repr call doesn't raise any exceptions
    assert repr(script.InsertOp([1, 2, 3], N("X", "X"), 42))
    assert repr(script.MoveOp([1, 2, 3], [4, 5, 6], 43))
    assert repr(script.UpdateOp([44, 45, 46], "foo"))
    assert repr(script.DeleteOp([23, 42, 12]))
