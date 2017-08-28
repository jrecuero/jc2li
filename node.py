from common import RuleHandler
from clierror import CliException

MODULE = 'NODE'


class Node(object):
    """Node class provides a container for every node in the syntax tree.
    """

    def __init__(self, theArgo, theParent=None, theLabel=None):
        """Node class initialization method.

        Args:
            theArgo (Argument): argument instance.
            theaParent (Node): parent node instance.
            theLabel (str): string to be used as label attribute.
        """
        self._parent = theParent
        self._children = list()
        self._argo = theArgo
        self._browsable = True
        self._label = theLabel if theLabel else self.Name
        self._loops = set()

    @property
    def Browsable(self):
        """Get property that return _browsable attribute.

        Only nodes that contains Argument information are browsable.

        Returns:
            boolean: True if Node is browsable, False else.
        """
        return self._browsable

    @property
    def Parent(self):
        """Get property that returns _parent attribute.

        Returns:
            Node: parent node instance in the syntax tree.
        """
        return self._parent

    @property
    def Parents(self):
        """Get property that returns _parents attribute.

        Returns:
            list: list with all parents for the node.
        """
        raise CliException(MODULE, 'parents() operation not allowed.')

    @Parent.setter
    def Parent(self, theParent):
        """Set property that sets a new parent for the node.

        Args:
            theParent (Node): node instance to use a a new parent.
        """
        self._parent = theParent

    @property
    def Argo(self):
        """Get property that returns _argo attribute.

        Returns:
            Argument: instance with the Argument attribute for the Node.
        """
        return self._argo

    @property
    def Children(self):
        """Get property that returns _children attribute.

        Returns:
            list: list with all node children.
        """
        return self._children

    @property
    def ArgoNode(self):
        return [self, ]

    def getChildrenNodes(self, **kwargs):
        children = []
        noLoop = kwargs.pop('theMatched') if kwargs.get('theNoLoop', None) else False
        for child in self.traverseChildren(theNoLoop=noLoop):
            children.extend(child.ArgoNode)
        return children

    @property
    def Siblings(self):
        """Get property that returns a list with all sibling nodes.

        Returns:
            list: list with all Nodes that are sibling in the syntax tree.
        """
        if self.parent and self.parent.hasChildren():
            return self.parent.Children
        else:
            return list()

    @property
    def Label(self):
        """Get property that returns _label attribute.

        Returns:
            str: string with the node label.
        """
        return self._label

    @Label.setter
    def Label(self, theValue):
        """Set property that assign a new value for _label atttibute.

        Args:
            theValue (str): new value to be assigned to the _label attribute.
        """
        self.Label = theValue

    @property
    def Name(self):
        """Get property that returns node name.

        Returns:
            str: string with the argument name.
        """
        return self.Argo.Name if self.Argo else None

    @property
    def Type(self):
        """Get property that returns node type.

        Returns:
            type: type for the argument contained in the node.
        """
        return self.Argo.Type if self.Argo else None

    @property
    def Default(self):
        """Get property that returns node default value.

        Returns:
            object: default value for the argument in the node.
        """
        return self.Argo.Default if self.Argo else None

    @property
    def Ancestor(self):
        """Get property that returns the node ancestor (parent).

        Returns:
            Node: node parent instance.
        """
        return self.parent

    @property
    def Ancestors(self):
        """Get property that returns a list with all ancestors.

        Returns:
            list: list with all ancestors, parent of parent of ...
        """
        allAncestors = list()
        traverse = self.parent
        while traverse:
            allAncestors.append(traverse)
            traverse = traverse.Ancestor
        return allAncestors

    def _addChild(self, theChild, theIsLoop=False):
        """Internal method that adds a new child Node to the Node.

        Args:
            theChild (Node): node to be added as a child.
            theIsLoop (boolean): True if child in a loop path.

        Returns:
            None
        """
        self.Children.append(theChild)
        theChild.parent = self
        if theIsLoop:
            self._loops.add(theChild)

    def addChild(self, theChild, theIsLoop=False):
        """Method that adds a new child Node to the Node.

        Args:
            theChild (Node): node to be added as a child.
            theIsLoop (boolean): True if child in a loop path.

        Returns:
            None
        """
        if theChild.Parent:
            raise CliException(MODULE, 'addChild() not allowed on child with parent.')
        else:
            self._addChild(theChild, theIsLoop)

    def childrenNames(self):
        """Method that returns a list with the name for all children.

        Returns:
            list: list with all children names.
        """
        return [child.Name for child in self.traverseChildren()]

    def childrenTypes(self):
        """Method that returns a list with the type for all children.

        Returns:
            list: list with all children types.
        """
        return [child.Type for child in self.traverseChildren()]

    def isRoot(self):
        """Method that returns if the Node is the root node.

        Returns:
            boolean: True if the node is the root node, False else.
        """
        return self.Parent is None

    def hasChildren(self):
        """Method that returns if the node has children.

        Returns:
            int: numnber of children for node.
        """
        return len(self.Children) > 0

    def hasSiblings(self):
        """Method that returns in the node has siblings in the syntax tree.

        Returns:
            int: number of siblings for the node.
        """
        return self.Parent and self.Parent.hasChildren()

    def traverseChildren(self, theNoLoop=False):
        """Method that traverse all node children.

        Args:
            theNoLoop (bool): True will avoid any child that is a loop path.

        Returns:
            generator: it returns a generator to be used in an iterator.
        """
        children = self.Children if not theNoLoop else [x for x in self.Children if not self.isLoopChild(x)]
        for child in children:
            yield child

    def traverseSiblings(self):
        """Method that traverse all siblings

        Returns:
            generator: it returns a generator to be used in an iterator.
        """
        for sibling in self.Siblings:
            yield sibling

    def traverseAncestors(self):
        """Method that traverse all ancestors.

        Returns:
            generator: it returns a generator to be used in an iterator.
        """
        for ancestor in self.Ancestors:
            yield ancestor

    def findByName(self, theName, **kwargs):
        """Method that checks if the node has the given name

        When looking for nodes in a path from the arguments passed in the
        command line, required arguments don't use the argument name, just
        the value, when looking for those in the parsing tree, they will not
        be found, but such as a mandatory and positional arguments, they
        should be a direct match for the direct position, that is the reason
        whe use the argument theCheckDefault=True when we want to make a path
        search, for any other scenario, where just the argument name will be
        used, set that argument to False.

        Args:
            theName (str): string with the node name.
            theCheckDefault (boolean): if True validates the node if it has a
            valid Default attribute (not None).

        Returns:
            Node: Node with the given name, None is not found.
        """
        if kwargs.get('theCheckDefault', None) and self.Default is None:
            return self
        return self if self.Name == theName else None

    def findChildByName(self, theName, **kwargs):
        """Method that returns the children node with the given name.

        Args:
            theName (str): string with the node name.
        """
        for child in self.traverseChildren():
            foundNode = child.findByName(theName, **kwargs)
            if foundNode is not None:
                return foundNode
        return None

    def isAnyChildBrowsable(self):
        """Method that returns if the node has any children that is
        browsable.

        Returns:
            boolean: True if there is any browsable child, False else.
        """
        for child in self.traverseChildren():
            if child.browsable:
                return True
        return False

    def isLoop(self):
        """Method that returns if the node is a loop node.

        Returns:
            boolean: True if it is a loop node, False else.
        """
        return False

    def isLoopChild(self, theChild):
        """Method that returns if the node has any child that is a loop.

        Returns:
            boolean: True if the node has loop child, False else.
        """
        return theChild in self._loops

    def findPath(self, thePathPatterns):
        """Method that given a list of strings, finds a path in the syntax
        tree.

        The list of strings is the command line input, and it contains all
        argument values for a given command, which syntax is used as the
        syntax tree.

        The Argorithm traverse the syntax tree matching every argument and
        returning the Node that contains every argument, if it is found.

        Args:
            thePathPatterns (list): list with the command line input.

        Returns:
            list: list with Node for every argument found in the input pattern.
        """
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
                raise CliException(MODULE, '<{}> not found'.format(pattern))
            else:
                nodePath.append(trav)
        return nodePath

    def buildChildrenNodeFromRule(self, theRule, theArgs):
        """Method that returns a child node under the given node for the
        given rule.

        child is the Node that has to be added inmidiatly.
        endChild is the Node that has to be returned as the next node in the
        sequence. For OnlyOneRule or endDrule it does not matter, because it
        the same node, but for any other rule that includes Hook, child will
        be the first/start hook, and next child will be last/end hook.

        Args:
            theRule (dict): dictionay with a syntax rule.
            theArgs (Arguments): command Arguments instance.

        Returns:
            Node: child node that matches the syntax rule.
        """
        if RuleHandler.isOnlyOneRule(theRule):
            child = Node(theArgs.getArgoFromName(RuleHandler.getArgsFromRule(theRule)), theParent=self)
            endChild = child
        elif RuleHandler.isEndRule(theRule):
            child = End(theParent=self)
            endChild = child
        elif RuleHandler.isZeroOrOneRule(theRule) or RuleHandler.isOnlyOneOptionRule(theRule):
            child = Hook(theParent=self, theLabel="Hook-Start")
            endChild = Hook(theLabel="Hook-End")
            endChild = child.buildHookFromRule(RuleHandler.getArgsFromRule(theRule), theArgs, endChild)
            if RuleHandler.isZeroOrOneRule(theRule):
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
            raise CliException(MODULE, 'Unkown type of rule.')

        self.addChild(child)
        return endChild

    def findNodes(self):
        """Method that returns all nodes to be traversed.

        Returns:
            list: list with all nodes to be traversed underneath the given
            node.
        """
        nodes = [self, ]
        for child in self.traverseChildren():
            nodes += child.findNodes()
        return nodes

    def _toString(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}Node.{}\n".format(indent, self.Label)

    def toStr(self, level):
        """Method that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        st = self._toString(level)
        for child in self.traverseChildren(theNoLoop=True):
            st += child.toStr(level + 1)
        return st

    def __str__(self):
        """Method that returns the string to be used when converting the
        instance to string.

        Returns:
            str: string with node information.
        """
        return self.toStr(0)


class Hook(Node):
    """Hook class provides a container for every node that not contains any
    argument information but is used to provides different branches in the
    syntax tree.
    """

    def __init__(self, theParent=None, theLabel=None):
        """Hook class initialization method.

        Args:
            theaParent (Node): parent node instance.
            theLabel (str): string to be used as label attribute.
        """
        super(Hook, self).__init__(None, theParent)
        self._browsable = False
        if theParent is None:
            self._parent = []
        else:
            self._parent = [self._parent, ]
        self._label = theLabel if theLabel else "Hook"

    @property
    def Parent(self):
        """Get property that returns _parent attribute.

        Returns:
            Node: parent node instance in the syntax tree.
        """
        return None

    @Parent.setter
    def Parent(self, theParent):
        """Set property that sets a new parent for the node.

        Args:
            theParent (Node): node instance to use a a new parent.
        """
        self._parent.append(theParent)

    @property
    def Ancestor(self):
        """Get property that returns the node ancestor (parent).

        Returns:
            Node: node parent instance.
        """
        return None

    @property
    def Parents(self):
        """Get property that returns _parents attribute.

        Returns:
            list: list with all parents for the node.
        """
        return self._parent

    @property
    def Name(self):
        """Get property that returns node name.

        Returns:
            str: string with the argument name.
        """
        return None

    @property
    def Type(self):
        """Get property that returns node type.

        Returns:
            type: type for the argument contained in the node.
        """
        return None

    @property
    def Default(self):
        """Get property that returns node default value.

        Returns:
            object: default value for the argument in the node.
        """
        return None

    @property
    def ArgoNode(self):
        return self.getChildrenNodes()

    def addChild(self, theChild, theIsLoop=False):
        """Method that adds a new child Node to the Node.

        Args:
            theChild (Node): node to be added as a child.
            theIsLoop (boolean): True if child in a loop path.

        Returns:
            None
        """
        self._addChild(theChild, theIsLoop)

    def findByName(self, theName, **kwargs):
        """Method that checks if the node has the given name

        When looking for nodes in a path from the arguments passed in the
        command line, required arguments don't use the argument name, just
        the value, when looking for those in the parsing tree, they will not
        be found, but such as a mandatory and positional arguments, they
        should be a direct match for the direct position, that is the reason
        whe use the argument theCheckDefault=True when we want to make a path
        search, for any other scenario, where just the argument name will be
        used, set that argument to False.

        Args:
            theName (str): string with the node name.
            theCheckDefault (boolean): if True validates the node if it has a
            valid Default attribute (not None).

        Returns:
            Node: Node with the given name, None is not found.
        """
        return self.findChildByName(theName, **kwargs)

    def buildHookFromRule(self, theRule, theArgs, theEndHook):
        """Method that build a sequence of nodes for the given rule.

        Args:
            theRule (dict): dictionary with the rule to use.
            theArgs (Arguments): command Argumets instance.
            theEndHook (Node): node that will be the last node.

        Returns:
            Node: Last node for the sequence being created.
        """
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
        """Method that returns all nodes to be traversed.

        Returns:
            list: list with all nodes to be traversed underneath the given
            node.
        """
        nodes = list()
        for child in self.traverseChildren():
            nodes += child.findNodes()
        return nodes

    def _toString(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}Hook.{}\n".format(indent, self.Label)


class Loop(Hook):
    """Loop class provides a container for every node that not contains any
    argument information but is used to provides different loops in the
    syntax tree.
    """

    def __init__(self, theParent=None, theLabel=None):
        """Loop class initialization method.

        Args:
            theaParent (Node): parent node instance.
            theLabel (str): string to be used as label attribute.
        """
        super(Loop, self).__init__(None, theLabel)
        self._label = theLabel if theLabel else "Loop"

    def isLoop(self):
        """Method that returns if the node is a loop node.

        Returns:
            boolean: True if it is a loop node, False else.
        """
        return True

    def _toString(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}Loop.{}\n".format(indent, self.Label)

    def getChildrenNodes(self, **kwargs):
        if kwargs.get('theMatched', None):
            kwargs.pop('theMatched')
            kwargs.setdefault('theNoLoop', True)
        else:
            kwargs.setdefault('theMatched', True)
            kwargs.setdefault('theNoLoop', False)
        return super(Loop, self).getChildrenNodes(**kwargs)

    def findChildByName(self, theName, **kwargs):
        """Method that returns the children node with the given name.

        Args:
            theName (str): string with the node name.
            theMatched (boolean): True if the node was already traverse,
            False else.
        """
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
    """Start class provides a container for every node that not contains any
    argument information but is used to provides the root node fo the syntax
    tree.
    """

    def __init__(self, theParent=None, theLabel=None):
        """Start class initialization method.

        Args:
            theaParent (Node): parent node instance.
            theLabel (str): string to be used as label attribute.
        """
        super(Start, self).__init__(None, theLabel)
        self._label = theLabel if theLabel else "Start"

    def _toString(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}Start.{}\n".format(indent, self.Label)


class End(Hook):
    """Start class provides a container for every node that not contains any
    argument information but is used to provides the last node fo the syntax
    tree.
    """

    def __init__(self, theParent=None, theLabel=None):
        """End class initialization method.

        Args:
            theaParent (Node): parent node instance.
            theLabel (str): string to be used as label attribute.
        """
        """
        """
        super(End, self).__init__(None, theLabel)
        self._label = theLabel if theLabel else "End"

    def buildHookFromRule(self, theRule, theArgs, theEndHook):
        """Method that build a sequence of nodes for the given rule.

        Args:
            theRule (dict): dictionary with the rule to use.
            theArgs (Arguments): command Argumets instance.
            theEndHook (Node): node that will be the last node.

        Returns:
            Node: Last node for the sequence being created.
        """
        raise TypeError('Error: End : can not build nodes after end')

    def _toString(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}End.{}\n".format(indent, self.Label)


if __name__ == '__main__':
    pass
