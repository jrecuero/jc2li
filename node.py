from common import _HANDLE_ERROR, RuleHandler


class Node(object):

    def __init__(self, theArgo, theParent=None, theLabel=None):
        self._parent = theParent
        self._children = list()
        self._argo = theArgo
        self._browsable = True
        self._label = theLabel if theLabel else self.Name
        self._loops = set()

    @property
    def Browsable(self):
        return self._browsable

    @property
    def Parent(self):
        return self._parent

    @property
    def Parents(self):
        return _HANDLE_ERROR('Error:  Node: parents() operation not allowed.')

    @Parent.setter
    def Parent(self, theParent):
        self._parent = theParent

    @property
    def Argo(self):
        return self._argo

    @property
    def Children(self):
        return self._children

    @property
    def Siblings(self):
        if self.parent and self.parent.hasChildren():
            return self.parent.Children
        else:
            return list()

    @property
    def Label(self):
        return self._label

    @Label.setter
    def Label(self, theValue):
        self.Label = theValue

    @property
    def Name(self):
        return self.Argo.Name if self.Argo else None

    @property
    def Type(self):
        return self.Argo.Type if self.Argo else None

    @property
    def Default(self):
        return self.Argo.Default if self.Argo else None

    @property
    def Ancestor(self):
        return self.parent

    @property
    def Ancestors(self):
        allAncestors = list()
        traverse = self.parent
        while traverse:
            allAncestors.append(traverse)
            traverse = traverse.Ancestor
        return allAncestors

    def _addChild(self, theChild, theIsLoop=False):
        self.Children.append(theChild)
        theChild.parent = self
        if theIsLoop:
            self._loops.add(theChild)

    def addChild(self, theChild, theIsLoop=False):
        if theChild.Parent:
            return _HANDLE_ERROR('Error:  Node: addChild() not allowed on child with parent.')
        else:
            self._addChild(theChild, theIsLoop)

    def childrenNames(self):
        return [child.Name for child in self.traverseChildren()]

    def childrenTypes(self):
        return [child.Type for child in self.traverseChildren()]

    def isRoot(self):
        return self.Parent is None

    def hasChildren(self):
        return len(self.Children) > 0

    def hasSiblings(self):
        return self.Parent and self.Parent.hasChildren()

    def traverseChildren(self, theNoLoop=False):
        children = self.Children if not theNoLoop else [x for x in self.Children if not self.isLoopChild(x)]
        for child in children:
            yield child

    def traverseSiblings(self):
        for sibling in self.Siblings:
            yield sibling

    def traverseAncestors(self):
        for ancestor in self.Ancestors:
            yield ancestor

    def findByName(self, theName, **kwargs):
        """
        When looking for nodes in a path from the arguments passed in the
        command line, required arguments don't use the argument name, just
        the value, when looking for those in the parsing tree, they will not
        be found, but such as a mandatory and positional arguments, they
        should be a direct match for the direct position, that is the reason
        whe use the argument theCheckDefault=True when we want to make a path
        search, for any other scenario, where just the argument name will be
        used, set that argument to False.
        """
        if kwargs.get('theCheckDefault', None) and self.Default is None:
            return self
        return self if self.Name == theName else None

    def findChildByName(self, theName, **kwargs):
        for child in self.traverseChildren():
            foundNode = child.findByName(theName, **kwargs)
            if foundNode is not None:
                return foundNode
        return None

    def isAnyChildBrowsable(self):
        for child in self.traverseChildren():
            if child.browsable:
                return True
        return False

    def isLoop(self):
        return False

    def isLoopChild(self, theChild):
        return theChild in self._loops

    def findPath(self, thePathPatterns):
        nodePath = []
        trav = self
        for pattern in thePathPatterns:
            if '=' in pattern:
                name, _ = pattern.split("=")
                checkDefault = False
            else:
                checkDefault = True
                name = pattern
            trav = trav.findChildByName(name, theCheckDefault=checkDefault)
            if trav is None:
                return _HANDLE_ERROR('<{}> not found'.format(pattern))
            else:
                nodePath.append(trav)
        return nodePath

    def buildChildrenNodeFromRule(self, theRule, theArgs):
        """
        child is the Node that has to be added inmidiatly.
        endChild is the Node that has to be returned as the next node in the
        sequence. For OnlyOneRule or endDrule it does not matter, because it
        the same node, but for any other rule that includes Hook, child will
        be the first/start hook, and next child will be last/end hook.
        """
        if RuleHandler.isOnlyOneRule(theRule):
            child = Node(theArgs.getArgoFromName(RuleHandler.getArgsFromRule(theRule)), theParent=self)
            endChild = child
        elif RuleHandler.isEndRule(theRule):
            child = End(theParent=self)
            endChild = child
        elif RuleHandler.isZeroOrOneRule(theRule):
            child = Hook(theParent=self, theLabel="Hook-Start")
            endChild = Hook(theLabel="Hook-End")
            endChild = child.buildHookFromRule(RuleHandler.getArgsFromRule(theRule), theArgs, endChild)
            child.addChild(endChild)
        elif RuleHandler.isZeroOrMoreRule(theRule) or RuleHandler.isOneOrMoreRule(theRule):
            child = Hook(theParent=self, theLabel="Hook-Start")
            loopChild = Loop(theParent=self, theLabel="Hook-Loop")
            endChild = Hook(theParent=self, theLabel="Hook-End")
            loopChild = child.buildHookFromRule(RuleHandler.getArgsFromRule(theRule), theArgs, loopChild)
            loopChild.addChild(endChild)
            loopChild.addChild(child, theIsLoop=True)
            if RuleHandler.isZeroOrMoreRule(theRule):
                child.addChild(endChild)
        else:
            return _HANDLE_ERROR('Error:  Node: Unkown type of rule.')
        self.addChild(child)
        return endChild

    def findNodes(self):
        nodes = [self, ]
        for child in self.traverseChildren():
            nodes += child.findNodes()
        return nodes

    def _toString(self, level):
        indent = "--" * level
        return "{}Node.{}\n".format(indent, self.Label)

    def toStr(self, level):
        st = self._toString(level)
        for child in self.traverseChildren(theNoLoop=True):
            st += child.toStr(level + 1)
        return st

    def __str__(self):
        return self.toStr(0)


class Hook(Node):

    def __init__(self, theParent=None, theLabel=None):
        super(Hook, self).__init__(None, theParent)
        self._browsable = False
        if theParent is None:
            self._parent = []
        else:
            self._parent = [self._parent, ]
        self._label = theLabel if theLabel else "Hook"

    @property
    def Parent(self):
        return None

    @Parent.setter
    def Parent(self, theParent):
        self._parent.append(theParent)

    @property
    def Ancestor(self):
        return None

    @property
    def Parents(self):
        return self._parent

    @property
    def Name(self):
        return None

    @property
    def Type(self):
        return None

    @property
    def Default(self):
        return None

    def addChild(self, theChild, theIsLoop=False):
        self._addChild(theChild, theIsLoop)

    def findByName(self, theName, **kwargs):
        return self.findChildByName(theName, **kwargs)

    def buildHookFromRule(self, theRule, theArgs, theEndHook):

        def addGrantChild(child, grantchild):
            if child:
                child.addChild(grantchild)

        if type(theRule) in [list, dict]:
            child = None
            for rule in theRule:
                if RuleHandler.isEndRule(rule):
                    raise TypeError('Error : Hook : endpoint not allowed in rule')
                if RuleHandler.getCounterFromRule(rule) == 0:
                    addGrantChild(child, theEndHook)
                    child = self.buildChildrenNodeFromRule(rule, theArgs)
                else:
                    grantchild = child.buildChildrenNodeFromRule(rule, theArgs)
                    child.addChild(grantchild)
                    child = grantchild
            addGrantChild(child, theEndHook)
            return theEndHook
        else:
            raise TypeError('Error: Hook : node requires a list of rules')

    def findNodes(self):
        nodes = list()
        for child in self.traverseChildren():
            nodes += child.findNodes()
        return nodes

    def _toString(self, level):
        indent = "--" * level
        return "{}Hook.{}\n".format(indent, self.Label)


class Loop(Hook):

    def __init__(self, theParent=None, theLabel=None):
        super(Loop, self).__init__(None, theLabel)
        self._label = theLabel if theLabel else "Loop"

    def isLoop(self):
        return True

    def _toString(self, level):
        indent = "--" * level
        return "{}Loop.{}\n".format(indent, self.Label)

    def findChildByName(self, theName, **kwargs):
        if kwargs.get('theMatched', None):
            kwargs.pop('theMatched')
            noLoop = True
        else:
            kwargs.setdefault('theMatched', True)
            noLoop = False
        for child in self.traverseChildren(theNoLoop=noLoop):
            foundNode = child.findByName(theName, **kwargs)
            if foundNode is not None:
                return foundNode
        return None


class Start(Hook):

    def __init__(self, theParent=None, theLabel=None):
        super(Start, self).__init__(None, theLabel)
        self._label = theLabel if theLabel else "Start"

    def _toString(self, level):
        indent = "--" * level
        return "{}Start.{}\n".format(indent, self.Label)


class End(Hook):

    def __init__(self, theParent=None, theLabel=None):
        super(End, self).__init__(None, theLabel)
        self._label = theLabel if theLabel else "End"

    def buildHookFromRule(self, theRule, theArgs, theEndHook):
        raise TypeError('Error: End : can not build nodes after end')

    def _toString(self, level):
        indent = "--" * level
        return "{}End.{}\n".format(indent, self.Label)


if __name__ == '__main__':
    pass
