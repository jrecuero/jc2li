from common import _HANDLE_ERROR, RuleHandler


class Node(object):

    def __init__(self, theArgo, theParent=None, theLabel=None):
        self._parent = theParent
        self._children = list()
        self._argo = theArgo
        self._browsable = True
        self._label = theLabel if theLabel else self.name

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

    @label.setter
    def label(self, theValue):
        self.label = theValue

    @property
    def name(self):
        return self.argo.Name if self.argo else None

    @property
    def type(self):
        return self.argo.Type if self.argo else None

    @property
    def default(self):
        return self.argo.Default if self.argo else None

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
        return [child.name for child in self.traverseChildren()]

    def childrenTypes(self):
        return [child.type for child in self.traverseChildren()]

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

    def findByName(self, theName, theCheckDefault=False):
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
        if theCheckDefault and self.default is None:
            return self
        return self if self.name == theName else None

    def findChildByName(self, theName, theCheckDefault=False):
        for child in self.traverseChildren():
            foundNode = child.findByName(theName, theCheckDefault)
            if foundNode is not None:
                return foundNode
        return None

    def isAnyChildBrowsable(self):
        for child in self.traverseChildren():
            if child.browsable:
                return True
        return False

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
                raise NameError('<{}> not found'.format(pattern))
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
            endChild = child.buildHookFromRule(RuleHandler.getArgsFromRule(theRule), theArgs)
            child.addChild(endChild)
        elif RuleHandler.isZeroOrMoreRule(theRule) or RuleHandler.isOneOrMoreRule(theRule):
            hookToEnd = True if RuleHandler.isZeroOrMoreRule(theRule) else False
            endChild = Hook(theParent=self, theLabel="Hook-End")
            child = Hook(theParent=self, theLabel="Hook-Start")
            loopHook = child.buildHookFromRule(RuleHandler.getArgsFromRule(theRule),
                                               theArgs,
                                               theHookToEnd=hookToEnd)
            loopHook._label = "Hook-Loop"
            loopHook.addChild(endChild)
            loopHook.addChild(child)
            if hookToEnd:
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
        return "{}Node.{}\n".format(indent, self.label)

    def toStr(self, level):
        st = self._toString(level)
        for child in self.traverseChildren():
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
    def parent(self):
        return None

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
    def type(self):
        return None

    @property
    def default(self):
        return None

    def addChild(self, theChild):
        self._addChild(theChild)

    def findByName(self, theName, theCheckDefault=False):
        return self.findChildByName(theName, theCheckDefault)

    def buildHookFromRule(self, theRule, theArgs, theHookToEnd=True):

        def addGrantChild(child, grantchild):
            if child:
                child.addChild(grantchild)

        endHook = Hook(theLabel="Hook-End")
        if type(theRule) in [list, dict]:
            child = None
            for rule in theRule:
                if RuleHandler.isEndRule(rule):
                    raise TypeError('Error : Hook : endpoint not allowed in rule')
                if RuleHandler.getCounterFromRule(rule) == 0:
                    addGrantChild(child, endHook)
                    child = self.buildChildrenNodeFromRule(rule, theArgs)
                else:
                    grantchild = child.buildChildrenNodeFromRule(rule, theArgs)
                    child.addChild(grantchild)
                    child = grantchild
            addGrantChild(child, endHook)
            # if theHookToEnd:
            #     self.addChild(endHook)
            return endHook
        else:
            raise TypeError('Error: Hook : node requires a list of rules')

    def findNodes(self):
        nodes = list()
        for child in self.traverseChildren():
            nodes += child.findNodes()
        return nodes

    def _toString(self, level):
        indent = "--" * level
        return "{}Hook.{}\n".format(indent, self.label)


class Start(Hook):

    def __init__(self, theParent=None, theLabel=None):
        super(Start, self).__init__(None, theLabel)
        self._label = theLabel if theLabel else "Start"

    def _toString(self, level):
        indent = "--" * level
        return "{}Start.{}\n".format(indent, self.label)


class End(Hook):

    def __init__(self, theParent=None, theLabel=None):
        super(End, self).__init__(None, theLabel)
        self._label = theLabel if theLabel else "End"

    def buildHookFromRule(self, theRule, theArgs):
        raise TypeError('Error: End : can not build nodes after end')

    def _toString(self, level):
        indent = "--" * level
        return "{}End.{}\n".format(indent, self.label)


if __name__ == '__main__':
    pass
