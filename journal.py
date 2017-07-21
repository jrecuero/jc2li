class Journal(object):

    def __init__(self):
        self._path = list()
        self._argos = dict()
        self._traverseNode = None
        self._root = None

    @property
    def root(self):
        return self._root

    @property
    def path(self):
        return self._path

    @property
    def argos(self):
        return self._argos

    @property
    def traverseNode(self):
        return self._traverseNode

    @traverseNode.setter
    def traverseNode(self, theNode):
        self._traverseNonde = theNode

    def addNode(self, theNode):
        if theNode:
            self.path.append(theNode)
            self.argos.update(theNode.argo)
            self.traverseNode = theNode

    def moveToChildByName(self, theNode, theName):
        childNode = theNode.findChildByName(theName)
        if childNode:
            self.addNode(childNode)
        return childNode


if __name__ == '__main__':
    pass
