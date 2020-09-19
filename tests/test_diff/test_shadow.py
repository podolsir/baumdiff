from baumdiff.simpletree import Node
from baumdiff.shadow import ShadowNode
from ..utils import assertTreeEqual

N = Node 
SN = lambda x: N(x, x)


def test_shadow_add():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    st = ShadowNode.convert(t)
    st.add(SN("B1a"), 1)
    assert st.allchildren == st.children
    st.add(SN("B2a"), -1)
    assert st.allchildren == st.children

def test_shadow_delete_add_end():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    st = ShadowNode.convert(t)
    st.remove(len(st.children) - 1)
    st.add(SN("B1"), -1)
    assert st.children == [SN("A1"), SN("A2"), SN("B1")]
    assert st.allchildren == [SN("A1"), SN("A2"), SN("A3"), SN("B1")]

def test_shadow_delete_add_begin():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    st = ShadowNode.convert(t)
    st.remove(0)
    st.add(SN("B1"), 0)
    assert st.children == [SN("B1"), SN("A2"), SN("A3")]
    assert st.allchildren == [SN("A1"), SN("B1"), SN("A2"), SN("A3")]
    st.add(SN("B2"), 1)
    assert st.children == [SN("B1"), SN("B2"), SN("A2"), SN("A3")]
    assert st.allchildren == [SN("A1"), SN("B1"), SN("B2"), SN("A2"), SN("A3")]
    st.remove(2)
    st.add(SN("B3"), 2)
    assert st.children == [SN("B1"), SN("B2"), SN("B3"), SN("A3")]
    assert st.allchildren == [SN("A1"), SN("B1"), SN("B2"), SN("A2"), SN("B3"), SN("A3")]

def test_shadow_del_del():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    st = ShadowNode.convert(t)
    st.remove(0)
    st.remove(0)
    st.add(SN("B1"), 0)
    assert st.children == [SN("B1"), SN("A3")]
    assert st.allchildren == [SN("A1"), SN("A2"), SN("B1"), SN("A3")]
    st.remove(0)
    assert st.children == [SN("A3")]
    assert st.allchildren == [SN("A1"), SN("A2"), SN("B1"), SN("A3")]
    assert [x.status for x in st.allchildren] == [['deleted'], ['deleted'], ['inserted', 'deleted'], []]

def test_shadow_update():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    st = ShadowNode.convert(t)
    st[2].value = "Ax"
    assert st[2].value == "Ax"
    assert st.children == [SN("A1"), SN("A2"), N("A3", "Ax")]
    assert st.allchildren == [SN("A1"), SN("A2"), N("A3", "Ax")]
    assert [x.status for x in st.allchildren] == [[], [], ['updated']]

def test_shadow_clone():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    st = ShadowNode.convert(t)
    stc = st.clone(True)
    assertTreeEqual(st, stc)

def test_shadow_clone_no_children():
    t = N("R", "R", SN("A1"), SN("A2"), SN("A3"))
    st = ShadowNode.convert(t)
    stc = st.clone(False)
    assert st.id == stc.id
    assert st.value == stc.value
    assert len(stc.children) == 0
