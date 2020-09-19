import difflib
from .treeaccess import DefaultTreeAdapter
from .script import InsertOp, MoveOp, DeleteOp, UpdateOp

class NullProgressMonitor(object):
    def __init__(self):
        pass
    def progress(self, progress):
        pass

class Diff:
    def __init__(self, matcher, progress_monitor=None,
        tree_adapter=None,
        value_getter=None, value_setter=None, value_eq=None,
        parent_getter=None, path_getter=None,
        index_getter=None,
        child_add_func=None,
        child_remove_func=None,
        child_seq_func=None,
        clone_func=None):

        tree_adapter = tree_adapter or DefaultTreeAdapter()
        self.progress_monitor = progress_monitor or NullProgressMonitor()
        self.value_getter = value_getter or tree_adapter.get_value
        self.value_setter = value_setter or tree_adapter.set_value
        self.value_eq = value_getter or tree_adapter.value_eq
        self.parent_getter = parent_getter or tree_adapter.get_parent
        self.path_getter = path_getter or tree_adapter.get_path
        self.index_getter = index_getter or tree_adapter.get_index
        self.child_add_func = child_add_func or tree_adapter.add_child
        self.child_remove_func = child_remove_func or tree_adapter.remove_child
        self.child_seq_func = child_seq_func or tree_adapter.child_sequence
        self.clone_func = clone_func or tree_adapter.clone_node

        self.matcher = matcher

        self._marks1, self._marks2 = set(), set()

    def _postOrder(self, root, f, *args):
        for i in reversed(self.child_seq_func(root)):
            args = self._postOrder(i, f, *args)
            f(i, *args)
        return args

    def _reset(self):
        self._marks1, self.marks2 = set(), set()

    def _lcs(self, a, b):
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for op, i1, i2, j1, _ in sm.get_opcodes():
            if op != "equal":
                continue
            for x in range(i2 - i1):
                yield (i1 + x, j1 + x)
        
    def _mark(self, node1, node2):
        self._marks1.add(node1)
        self._marks2.add(node2)

    def _has_mark1(self, node1):
        return node1 in self._marks1

    def _has_mark2(self, node2):
        return node2 in self._marks2

    def _findPos(self, kid2, parent1):
        parent2 = self.parent_getter(kid2)
        pivot = -1
        S = self.child_seq_func
        for i in range(len(parent2)): # pragma: no branch
            if S(parent2)[i] == kid2:
                break
            if not self._has_mark2(S(parent2)[i]):
                continue
            pivot = i
        if pivot < 0: 
            return 0
        i = 0
        #print "pivot", pivot, parent2[pivot]

        while S(parent1)[i] != S(parent2)[pivot]:
            i += 1
        return i + 1

    def _align(self, node1, node2, matching, script, usemoves):
        S = self.child_seq_func

        def move(node, kid, newPos):
            oldPos = self.index_getter(node, kid)
            if newPos >= oldPos:
                newPos -= 1
            self.child_remove_func(node, oldPos)
            self.child_add_func(node, kid, newPos)

        (n1c, n2c) = set(S(node1)), set(S(node2))
        seq1 = [n for n in S(node1) if n in n2c]
        seq2 = [n for n in S(node2) if n in n1c]

        len_lcs = 0
        for (ai, bi) in self._lcs(seq1, seq2):
            self._mark(seq1[ai], seq2[bi])
            len_lcs += 1

        if (len_lcs == len(seq1) and len(seq1) == len(seq2)):
            return

        toMove = (x for x in seq1 if not self._has_mark1(x))
        for a in toMove:
            b = matching[a]
            newPos = self._findPos(b, node1)
            script.extend(self._getMove(a, self.path_getter(node1), newPos, usemoves))
            move(node1, a, newPos)
            self._mark(a, b)
        return

    def _delete(self, root, revMatching, script):
        if revMatching[root] is None:
            script.append(DeleteOp(self.path_getter(root)))
            parent = self.parent_getter(root)
            self.child_remove_func(parent, self.index_getter(parent, root))
        return [revMatching, script]

    def _pathFixup(self, deletePath, insertPath):
        # The deleted node is 'deeper' in the tree than the inserted node
        # so that it cannot possibly affect the insert path
        if len(deletePath) > len(insertPath):
            return insertPath
        newInsertPath = []
        for i in range(len(deletePath) - 1):
            if insertPath[i] != deletePath[i]:
                # the deleted node is in a region of a tree which cannot affect
                # the insert path, break off and return the original one
                return insertPath
            newInsertPath.append(insertPath)
        pathIndex = len(deletePath) - 1
        if deletePath[pathIndex] < insertPath[pathIndex]:
            # the deletion affects the insert path 
            # -> shift insert path component by -1 and append rest of the insert path
            newInsertPath.append(insertPath[pathIndex] - 1)
            newInsertPath.extend(insertPath[pathIndex + 1:])
            return newInsertPath
        # otherwise, just return the original path
        return insertPath

    def _getMove(self, node, targetParentPath, pos, usemoves):
        if usemoves:
            return (MoveOp(self.path_getter(node), targetParentPath, pos),)
        else:
            insertNode = self.clone_func(node, True)
            deletedNodePath = self.path_getter(node) 
            return (DeleteOp(deletedNodePath),
                    InsertOp(self._pathFixup(deletedNodePath, targetParentPath), insertNode, pos))
        
    def _core(self, root2, newMatching, revMatching, script, usemoves):
        partnerParent = newMatching[root2]

        # Align Phase (at the beginning as the algorithm
        # is shifted by a level compare to the original paper)
        # The result are the 'in-order' markings which are stored in a set; 
        # the side effect are move operations.
        self._align(partnerParent, root2, revMatching, script, usemoves)

        for node2 in root2:
            # Insert Phase
            if newMatching[node2] is None:
                # construct the new node
                newNode = self.clone_func(node2, False)
                # register it with the matching
                newMatching[node2] = newNode 
                
                # find a new position for the node and update the
                # in order markings
                pos = self._findPos(node2, partnerParent)
                self._mark(newNode, node2)

                # do the insertion
                # clone the node for storage in op so 
                # next insertions do not add children to it
                script.append(InsertOp(self.path_getter(partnerParent), 
                                    self.clone_func(newNode, False), 
                                    pos))
                self.child_add_func(partnerParent,newNode, pos)
            else:
                node1 = newMatching[node2]
                
                # Move Phase
                if partnerParent != self.parent_getter(node1):
                    # find a new position and update the markers
                    newPos = self._findPos(node2, partnerParent)
                    self._mark(node1, node2)
                    
                    # do the move
                    script.extend(self._getMove(node1, self.path_getter(partnerParent), newPos, usemoves))
                    parent1 = self.parent_getter(node1)
                    self.child_remove_func(parent1, self.index_getter(parent1, node1))
                    self.child_add_func(partnerParent, node1, newPos)

                # Update Phase
                v1, v2 = self.value_getter(node1), self.value_getter(node2)
                if not self.value_eq(v1, v2):
                    script.append(UpdateOp(self.path_getter(node1), v2))
                    self.value_setter(node1, v2)

    def edit_script(self, root1, root2, use_moves):
        self._reset()

        try:
            newMatching = dict(self.matcher.getMatching(root1, root2))    
            revMatching = self.matcher.getMatching(root2, root1)

            # breadth-first/preorder recursive traversal
            # Align/Insert/Move/Update Phases
            def update(level, script, progress):
                for i in level:
                    self._core(i, newMatching, revMatching, script, use_moves)
                    progress += 1
                    self.progress_monitor.progress(progress)
                newlevel = []
                for i in level:
                    newlevel.extend(self.child_seq_func(i))
                if len(newlevel) > 0:
                    update(newlevel, script, progress)

            # recursion kickoff
            script = []
            update([root2], script, 0)

            # Delete Phase (depth-first, last-child-first)
            self._postOrder(root1, self._delete, self.matcher.getMatching(root2, root1), script)
            
            return script
        finally:
            # Make sure not to keep references to the nodes
            self._reset()

def edit_script(root1, root2, matcher, progressmonitor=None, usemoves=True, **kwargs):
    return Diff(matcher=matcher, progress_monitor=progressmonitor).edit_script(root1, root2, use_moves=usemoves, **kwargs)
