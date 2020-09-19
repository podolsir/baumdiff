import random
import pytest

from baumdiff import simpletree

from ..utils import run_and_check_diff

N = simpletree.Node

@pytest.mark.slow
@pytest.mark.parametrize("usemoves", [True, False])
def test_randomtree_diff_100(usemoves):
    for _ in range(100):
        random.seed("test_diff_randomtrees_100")
        root1 = _generateRandomTree(1000)
        offset = random.randint(-10, 10)
        root2 = _generateRandomTree(1000 + offset)
        root2 = _updateValueRandomly(root2, 500)
        run_and_check_diff(root1, root2, usemoves=usemoves)

@pytest.mark.parametrize("usemoves", [True, False])
def test_randomtree_diff_10(usemoves):
    for _ in range(10):
        random.seed("test_diff_randomtrees")
        root1 = _generateRandomTree(1000)
        offset = random.randint(-10, 10)
        root2 = _generateRandomTree(1000 + offset)
        root2 = _updateValueRandomly(root2, 500)
        run_and_check_diff(root1, root2, usemoves=usemoves)

def _updateValueRandomly(tree, n):
    for _ in range(n):
        _pickRandomChild(tree).value += "_"
    return tree

def _pickRandomChild(root):
    if len(root.children) == 0:
        return root
    index = random.randrange(-1, len(root.children))
    if index == -1:
        return root
    return _pickRandomChild(root.children[index])

def _generateRandomTree(numNodes):
    root = N('R', 'R')
    total = 0

    nums = set(range(0, numNodes))
    while total < numNodes:
        n = random.sample(nums, 1)[0]
        nums.remove(n)
        node = N(str(n), str(n))
        p = _pickRandomChild(root)
        p.add(node)
        total += 1

    return root
