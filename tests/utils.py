from baumdiff import treediff
from baumdiff import simpletree as ST
from baumdiff.treeaccess import print_tree
from baumdiff.matcher import IdMatcher
from baumdiff.script import DefaultExecutor

def run_and_check_diff(root1, root2, usemoves):
    try:
        orig1 = root1.clone()
        orig2 = root2.clone()

        matcher = IdMatcher()
        pristine = root1.clone()
        script = treediff.edit_script(root1, root2, matcher, usemoves=usemoves)
        _assertTreeEqual(root1, root2)
        executor = DefaultExecutor()
        executor.execute(script, pristine)
        _assertTreeEqual(pristine, root2)
        script2 = treediff.edit_script(root1, root2, matcher, usemoves=usemoves)
        assert len(script2) == 0
        return script
    except Exception as e:
        try:
            print(_dumpTree(orig1))
            print(_dumpTree(orig2))
            print("Original trees:")
            print("Left:")
            print_tree(orig1)
            print("Right:")
            print_tree(orig2)
            from pprint import pprint
            pprint(script)

            print("Left in-place modified:")
            print_tree(root1)
            print("Left after script execution:")
            print_tree(pristine)
            print("Right (unchanged):")
            print_tree(root2)

            print("==================")
        finally:
            raise e

def _dumpTree(root):
    buf = ""
    def dumpNode(n, s):
        s = "N('{}', '{}', None, ".format(n.id, n.value)
        for i in n.children:
            s += dumpNode(i, s)
        s += "),"
        return s
    return dumpNode(root, buf)

def _assertTreeEqual(root1, root2):
    assert root1 == root2
    assert root1.children == root2.children
    for i in range(len(root1.children)):
        _assertTreeEqual(root1.children[i], root2.children[i])

assertTreeEqual = _assertTreeEqual