from collections import defaultdict

MARK_NONE = 0
MARK_REMOVE = 1

# Parent-Child-Successor Relation
# (relational representation of the tree structure)
class PCS(object):
    def __init__(self, parent, child, succ):
        (self.parent, self.child, self.succ) = (parent, child, succ)
        self.mark = MARK_NONE
        self.hash = self.hashCode()
    def __repr__(self): # pragma: no cover 
        # This is for internal debugging purposes only, no need to test
        return "pcs(%s, %s, %s)" % (
            repr(self.parent), repr(self.child), repr(self.succ))
    def __eq__(self, other):
        return (other is not None
                and other.parent == self.parent
                and other.child == self.child
                and other.succ == self.succ)
    def __hash__(self):
        return self.hash
    def hashCode(self):
        (h, b) = (38743907, 77916165)
        for i in (self.parent, self.child, self.succ):
            h = b + h * hash(i)
        return h

# c(n, 'c') relational (mapping between node ids and values)
class CNT(object):
    def __init__(self, node, content):
        (self.node, self.content) = (node, content)
        self.mark = MARK_NONE
        self.hash = self.hashCode()
    def hashCode(self):
        (h, b) = (49525371, 44667271)
        for i in (self.node, self.content):
            h = b + h * hash(i)
        return h
    def __repr__(self):
        return "c(%s, %s)" % (
            repr(self.node), repr(self.content))
    def __eq__(self, other):
        return (other is not None
                and other.node == self.node
                and other.content == self.content)
    def __hash__(self):
        return self.hash

class MergeIndex(object):
    # Encapsulates the different LUTs against
    # the core algorihtm
    def __init__(self, parentLUT, predLUT, succLUT, cntLUT):
        self.parentLUT = parentLUT
        self.predLUT = predLUT
        self.succLUT = succLUT
        self.cntLUT = cntLUT

    def _get(self, key, change, lut):
        items = lut[key]
        if len(items) <= 1:
            return None
        for i in items:
            if i.mark != MARK_REMOVE and i != change:
                return i
        return None

    def getOtherContent(self, change):
        if not isinstance(change, CNT):
            return None
        return self._get(change.node, change, self.cntLUT)

    def getOtherRoot(self, change):
        if not isinstance(change, PCS):
            return None
        return self._get((change.child, change.succ), change, self.parentLUT)

    def getOtherSuccessor(self, change):
        if not isinstance(change, PCS):
            return None
        return self._get((change.parent, change.child), change, self.succLUT)

    def getOtherPredecessor(self, change):
        if not isinstance(change, PCS):
            return None
        return self._get((change.parent, change.succ), change, self.predLUT)

# core tree -> relational conversion
def _convertToCPCS(node, index, result):
    result.add(CNT((node, index), node.value))
    if len(node.children) == 0:
        result.add(PCS((node, index), (None, index), (None, index)))
        return
    lastNode = None
    for i in range(len(node.children)):
        result.add(PCS((node, index),
                       (lastNode, index),
                       (node.children[i], index)))
        lastNode = node.children[i]
    result.add(PCS((node, index), (node.children[-1], index), (None, index)))

# converts a ordinary tree to the relational representation
def convertToCPCS(root, index, minOccurence):
    def update(level, result, mo):
        if len(level) == 0:
            return
        newlevel = []
        for i in level:
            _convertToCPCS(i, index, result)
            if i not in minOccurence:
                mo[i] = index
            newlevel.extend(i.children)
        update(newlevel, result, mo)

    result = set()
    result.add(PCS((None, index), (root, index), (None, index)))
    result.add(PCS((None, index), (None, index), (root, index)))
    update([root], result, minOccurence)
    return result

class MergeConflict(Exception):
    def __init__(self, change, otherChange):
        self.change = change
        self.otherChange = otherChange

# Helper functions for buildTStar
def _star(params, mo):
    newParams = []
    for (node, index) in params:
        if node is not None:
            newParams.append((node, min(index, mo[node])))
        else:
            newParams.append((node, 0))
    return tuple(newParams)

def pcsStar(pcs, mo):
    return PCS(*_star((pcs.parent, pcs.child, pcs.succ), mo))

def cntStar(cnt, mo):
    return CNT(_star((cnt.node,), mo)[0], cnt.content)

# Converts a raw relational tree representation
# to a set using class representatives (T*_i)
def buildTStar(t, mo):
    tstar = set()
    for i in t:
        if isinstance(i, PCS):
            tstar.add(pcsStar(i, mo))
        elif isinstance(i, CNT):
            tstar.add(cntStar(i, mo))
        else: # pragma: no cover
            raise ValueError
    return tstar

def buildLUTs(merged):
    # build the lookup tables for content, predecessor,
    # successor and parent lookup
    parentLUT = defaultdict(lambda: [])
    predLUT = defaultdict(lambda: [])
    succLUT = defaultdict(lambda: [])
    cntLUT = defaultdict(lambda: [])
    for i in merged:
        if isinstance(i, CNT):
            cntLUT[i.node].append(i)
        else:
            predLUT[(i.parent, i.succ)].append(i)
            succLUT[(i.parent, i.child)].append(i)
            if (i.child[0], i.succ[0]) != (None, None):
                parentLUT[(i.child, i.succ)].append(i)
    return (parentLUT, predLUT, succLUT, cntLUT)


def _conflict(change, iChange):
    raise MergeConflict(change, iChange)

def _core(t0star, rawMerged, mergeIndex):
    # core Lindholm algorithm
    iChange = None
    for change in rawMerged:
        if change.mark == MARK_REMOVE:
            continue
        m = mergeIndex
        for get in (m.getOtherContent,
                    m.getOtherRoot,
                    m.getOtherPredecessor,
                    m.getOtherSuccessor):
            iChange = get(change)
            if iChange is not None:
                break
        if iChange is not None:
            if iChange in t0star:
                iChange.mark = MARK_REMOVE
            elif change in t0star:
                change.mark = MARK_REMOVE
            else:
                _conflict(change, iChange)
    return [x for x in rawMerged if x.mark != MARK_REMOVE]

def reconstructTree(merged, mergeIndex):
    # build a node -> content look-up table
    # to update merged node values
    contentLUT = dict(((x.node, x.content) for x in merged if isinstance(x, CNT)))

    # Retrieves all children of the given subtree root,
    # adds their copies to the root (the original ones
    # are used as hash keys and must not be changed)
    # and additionally returns a list of found successors
    def update(root):
        # Level kick off: get the first successor x_0
        # i.e. a non-deleted entry x_0 such that pcs(root, -|, x_0)
        candsucc = mergeIndex.succLUT[root, (None, 0)]
        for i in candsucc: # pragma: no branch; this is never called for leaf nodes
            if i.mark != MARK_REMOVE:
                succ = i.succ
                break

        # main loop
        # in each iteration look for entry x_i+1
        # with pcs(root, x_i, x_i+1)
        # while x_i+1 != |-
        next = []
        while succ[0] is not None:
            newNode = (succ[0].clone(False), succ[1])
            newNode[0].value = contentLUT[newNode]
            root[0].add(newNode[0])
            next.append(newNode)
            candsucc = mergeIndex.succLUT[root, succ]
            for i in candsucc:
                if i.mark != MARK_REMOVE:
                    succ = i.succ
        return next

    # Root kick off:
    # The root is a (non-deleted) node R with the condition:
    # pcs(_, R, |-)
    candroot = mergeIndex.predLUT[(None, 0), (None, 0)]
    # We assume that the tree always has a root
    for i in candroot: # pragma: no branch
        if i.mark != MARK_REMOVE: # pragma: no branch
            root = i.child
        break
    newRoot = (root[0].clone(False), root[1])

    # breadth first, first child first iteration
    next = update(newRoot)
    while len(next) != 0:
        newnext = []
        for i in next:
            newnext.extend(update(i))
        next = newnext
    return newRoot[0]

def merge(root0, root1, root2):
    # convert the trees to the relational
    # representation and create the minimal
    # indices dictionary mo as a byproduct
    mo = {}
    t0 = convertToCPCS(root0, 0, mo)
    t1 = convertToCPCS(root1, 1, mo)
    t2 = convertToCPCS(root2, 2, mo)

    # use mo to build the T*_i sets
    # that use class representatives instead
    # of actual nodes
    t0star = buildTStar(t0, mo)
    t1star = buildTStar(t1, mo)
    t2star = buildTStar(t2, mo)

    # construct the initial merge (probably inconsistent)
    rawMerge = set()
    rawMerge.update(t0star)
    rawMerge.update(t1star)
    rawMerge.update(t2star)

    # create the lookup tables for the merge
    # for fast search for inconsistent changes
    (parentLUT, predLUT, succLUT, cntLUT) = buildLUTs(rawMerge)
    mergeIndex = MergeIndex(parentLUT, predLUT, succLUT, cntLUT)

    # Do the actual merge.
    # (That's about time after all that preprocessing)
    merged = _core(t0star, rawMerge, mergeIndex)

    # reconstruct the merged tree from the merged relational
    # representation and return it
    return reconstructTree(merged, mergeIndex)
