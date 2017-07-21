from common import _HANDLE_ERROR


class Node(object):

    def __init__(self, theArgo, theParent=None):
        self._parent = theParent
        self._children = list()
        self._argo = theArgo
        self._browsable = True
        self._label = self.name

    @property
    def browsable(self):
        return self._browsable

    @property
    def parent(self):
        return self._parent

    @property
    def parents(self):
        return _HANDLE_ERROR('Error:  Node: parents() operation not allowed.')

    @parent.setter
    def parent(self, theParent):
        self._parent = theParent

    @property
    def argo(self):
        return self._argo

    @property
    def children(self):
        return self._children

    @property
    def siblings(self):
        if self.parent and self.parent.hasChildren():
            return self.parent.children
        else:
            return list()

    @property
    def label(self):
        return self._label

    @property
    def name(self):
        return self.argo.name if self.argo else None

    @property
    def type(self):
        return self.argo.type if self.argo else None

    @property
    def default(self):
        return self.argo.default if self.argo else None

    @property
    def ancestor(self):
        return self.parent

    @property
    def ancestors(self):
        allAncestors = list()
        traverse = self.parent
        while traverse:
            allAncestors.append(traverse)
            traverse = traverse.ancestor
        return allAncestors

    def _addChild(self, theChild):
        self.children.append(theChild)
        theChild.parent = self

    def addChild(self, theChild):
        if theChild.parent:
            return _HANDLE_ERROR('Error:  Node: addChild() not allowed on child with parent.')
        else:
            self._addChild(theChild)

    def childrenNames(self):
        return [child.name for child in self.children]

    def childrenTypes(self):
        return [child.type for child in self.children]

    def isRoot(self):
        return self.parent is None

    def hasChildren(self):
        return len(self.children) > 0

    def hasSiblings(self):
        return self.parent and self.parent.hasChildren()

    def traverseChildren(self):
        for child in self.children:
            yield child

    def traverseSiblings(self):
        for sibling in self.siblings:
            yield sibling

    def traverseAncestors(self):
        for ancestor in self.ancestors:
            yield ancestor

    def findByName(self, theName):
        if self.name == theName:
            return self
        return None

    def findChildByName(self, theName):
        for child in self.traverseChildren():
            foundNode = child.findByName(theName)
            if foundNode is not None:
                return foundNode
        return None

    def isAnyChildBrowsable(self):
        for child in self.traverseChildren():
            if child.browsable:
                return True
        return False

    def findPath(self, pathPatterns):
        nodePath = []
        trav = self
        for pattern in pathPatterns:
            trav = trav.findChildByName(pattern)
            if trav is None:
                raise NameError('<{}> not found'.format(pattern))
            else:
                nodePath.append(trav)
        return nodePath


class Hook(Node):

    def __init__(self, theParent=None):
        super(Hook, self).__init__(None, theParent)
        self._browsable = False
        if theParent is None:
            self._parent = []
        else:
            self._parent = [self._parent, ]

    @property
    def parent(self):
        return _HANDLE_ERROR('Error: Hook: parent() operation not allowed.')

    @parent.setter
    def parent(self, theParent):
        self._parent.append(theParent)

    @property
    def ancestor(self):
        return None

    @property
    def parents(self):
        return self._parent

    @property
    def name(self):
        return None

    @property
    def label(self):
        return 'Hook'

    @property
    def type(self):
        return None

    @property
    def default(self):
        return None

    def addChild(self, theChild):
        self._addChild(theChild)

    def findByName(self, theName):
        return self.findChildByName(theName)


class Start(Hook):

    @property
    def label(self):
        return 'Start'


class End(Hook):

    @property
    def label(self):
        return 'End'


if __name__ == '__main__':
    pass