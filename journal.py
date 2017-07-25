import shlex
from common import _HANDLE_ERROR, RuleHandler
from common import ARGOS_ATTR, RULES_ATTR, TREE_ATTR
from node import Start


class Journal(object):

    def __init__(self):
        """
        """
        self._path = list()
        self._argos = dict()
        self._traverseNode = None
        self._root = None

    @property
    def Root(self):
        """
        """
        return self._root

    @property
    def Path(self):
        """
        """
        return self._path

    @property
    def Argos(self):
        """
        """
        return self._argos

    @property
    def TraverseNode(self):
        """
        """
        return self._traverseNode

    @TraverseNode.setter
    def TraverseNode(self, theNode):
        """
        """
        self.TraverseNode = theNode

    def addNode(self, theNode):
        """
        """
        if theNode:
            self.Path.append(theNode)
            self.Argos.update(theNode.argo)
            self.TraverseNode = theNode

    def moveToChildByName(self, theNode, theName):
        """
        """
        childNode = theNode.findChildByName(theName)
        if childNode:
            self.addNode(childNode)
        return childNode

    def buildCommandParsingTree(self, theFunc):
        """Build the command parsing tree using the command arguments and the
        command syntax.
        """
        root = Start()
        argos = getattr(theFunc, ARGOS_ATTR, None)
        if argos:
            argos.index()
            rules = getattr(theFunc, RULES_ATTR, list())
            trav = root
            for rule in rules:
                newTrav = trav.buildChildrenNodeFromRule(rule, argos)
                trav = newTrav
            setattr(theFunc, TREE_ATTR, root)
            return True
        return _HANDLE_ERROR("Error: Building Command Parsing Tree: arguments not defined")

    def getCmdAndCliArgos(self, theFun, theInst, theLine):
        """Retrieve the command arguments stored in the command function and
        provided by @argo and @argos decorators; and the arguments passed by
        the user in the command line.
        """
        cmdArgos = getattr(theFun, ARGOS_ATTR, None)
        if cmdArgos is None:
            return theFun(theInst, theLine)
        cmdArgos.index()
        cliArgos = shlex.split(theLine)
        return cmdArgos, cliArgos

    def mapPassedArgosToCommandArgos(self, theRoot, theCmdArgos, theCliArgos):
        """Using the command arguments and argument values passed by the user
        in the CLI, map those using the command parsing tree in order to generate
        all arguments to be passed to the command function.
        """
        nodePath = theRoot.findPath(theCliArgos)
        if nodePath:
            matchedNodes = list()
            for nod, val in zip(nodePath, theCliArgos):
                if '=' in val:
                    _, argValue = val.split('=')
                else:
                    argValue = val
                argValue = nod.Argo.Type._(argValue)
                if nod not in matchedNodes:
                    nod.Argo.Value = argValue
                else:
                    if type(nod.Argo.Value) == list:
                        nod.Argo.Value.append(argValue)
                    else:
                        nod.Argo.Value = [nod.Argo.Value, argValue]
                matchedNodes.append(nod)
            useArgs = theCmdArgos.getIndexedValues()
            return useArgs
        else:
            return _HANDLE_ERROR("Error: Path for arguments {} not found.".format(theCliArgos))

    def buildCommandArgumentsFromSyntax(self, theFunc, theInst, theLine):
        """
        """
        cmdArgos, cliArgos = self.getCmdAndCliArgos(theFunc, theInst, theLine)

        root = getattr(theFunc, TREE_ATTR, None)
        rules = getattr(theFunc, RULES_ATTR, None)
        if len(cliArgos) < RuleHandler.syntaxMinArgs(rules):
            return _HANDLE_ERROR("Error: Number of Args: Too few arguments")

        useArgs = self.mapPassedArgosToCommandArgos(root, cmdArgos, cliArgos)
        if useArgs is None:
            return _HANDLE_ERROR('Error: Incorrect arguments"')
        if not all(map(lambda x: x is not None, useArgs)):
            return _HANDLE_ERROR('Error: Mandatory argument is not present"')

        return useArgs


if __name__ == '__main__':
    pass
