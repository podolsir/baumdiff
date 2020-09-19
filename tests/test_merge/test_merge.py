from baumdiff.simpletree import Node
from baumdiff import treemerge

import pytest
from ..utils import assertTreeEqual

N = Node

def test_merge1():
    # Sample from Lindholm Paper 
    root0 = N('R', 'R',
              N('a', 'a',
                N('d', 'd'),
                N('e', 'e'),
                N('f', 'f'),
                ),
              N('b', 'b',
                N('g', 'g'),
                ),
              )

    root1 = N('R', 'R',
              N('b', 'b',
                N('g', 'g'),
                ),
              N('a', 'a',
                N('d', 'd'),
                N('e', 'e'),
                N('f', 'f'),
                ),
              N('i', 'i'),
              )

    root2 = N('R', 'R',
              N('a', 'a',
                N('e', 'e'),
                N('d', 'd'),
                N('f', 'f'),
                ),
              N('b', 'bx',
                ),
              )

    expected = N('R', 'R',
              N('b', 'bx',
                ),
              N('a', 'a',
                N('e', 'e'),
                N('d', 'd'),
                N('f', 'f'),
                ),
              N('i', 'i'),
              )
    merged = treemerge.merge(root0, root1, root2)
    assertTreeEqual(merged, expected)
  
def test_conflict():
    root0 = N('R', 'R', 
              N('C4', 'V4'),
              N('C1', 'V1'), 
              N('C3', 'V3'),
              N('CX', 'VX', 
                N('CX1', 'VX1'),
                N('CX2', 'VX1'),
                N('CX3', 'VX1'),
                N('CX4', 'VX1'),
                ),
              N('C2', 'V2'), 
              )
    root1 = N('R', 'R', 
              N('C4', 'V4'),
              N('C1', 'V1'), 
              N('C3', 'V3'),
              N('CX', 'VX', 
                N('CX1', 'VY1'),
                N('CX3', 'VX1'),
                N('CX2', 'VX1'),
                N('CX4', 'VX1'),
                ),
              N('C2', 'V2'), 
              )
    root2 = N('R', 'R', 
              N('C4', 'V4'),
              N('C1', 'VY2'), 
              N('C3', 'V3'),
              N('CX', 'VX', 
                N('CX1', 'VY2'),
                N('CX2', 'VX1'),
                N('CX3', 'VX1'),
                N('CX4', 'VX1'),
                ),
              N('C2', 'V2'), 
              )
    with pytest.raises(treemerge.MergeConflict) as excinfo:
        _ = treemerge.merge(root0, root1, root2)
    print(excinfo)