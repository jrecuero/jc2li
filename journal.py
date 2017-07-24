class Journal(object):

    def __init__(self):
        self._path = list()
        self._argos = dict()
        self._traverseNode = None
        self._root = None

    @property
    def Root(self):
        return self._root

    @property
    def Path(self):
        return self._path

    @property
    def Argos(self):
        return self._argos

    @property
    def TraverseNode(self):
        return self._traverseNode

    @TraverseNode.setter
    def TraverseNode(self, theNode):
        self.TraverseNode = theNode

    def addNode(self, theNode):
        if theNode:
            self.Path.append(theNode)
            self.Argos.update(theNode.argo)
            self.TraverseNode = theNode

    def moveToChildByName(self, theNode, theName):
        childNode = theNode.findChildByName(theName)
        if childNode:
            self.addNode(childNode)
        return childNode


if __name__ == '__main__':
    pass
