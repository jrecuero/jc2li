import shlex
from common import RuleHandler
from common import ARGOS_ATTR, RULES_ATTR, TREE_ATTR
from node import Start
from clierror import CliException

MODULE = 'JOURNAL'


class Journal(object):
    """Journal class that provides a container with all matching required for
    checking if the commmand syntax is valid and napping arguments entered in
    the command line with command arguments.
    """

    def __init__(self):
        """Journal class initialization method.
        """
        self._path = list()
        self._argos = dict()
        self._traverseNode = None
        self._root = None

    @property
    def Root(self):
        """Get property that returns _root attribute.

        Returns:
            Node: root node instance.
        """
        return self._root

    @property
    def Path(self):
        """Get property that returns _path attribute.

        Returns:
            list: list with all nodes in a path.
        """
        return self._path

    @property
    def Argos(self):
        """Get property that returns _argos attribute.

        Return:
            Arguments: Arguments instance with all command arguments.
        """
        return self._argos

    @property
    def TraverseNode(self):
        """Get property that returns _traverseNode attribute.

        Returns:
            Node: Node being traversed at any point.
        """
        return self._traverseNode

    @TraverseNode.setter
    def TraverseNode(self, theNode):
        """Set property that assigns a value to the _traverseNode attibute.

        Args:
            theNode (Node): new Node instance to assign as a traverse node.
        """
        self.TraverseNode = theNode

    def addNode(self, theNode):
        """Method that adds a new node.

        Args:
            theNode (Node): node instance to be added.
        """
        if theNode:
            self.Path.append(theNode)
            self.Argos.update(theNode.argo)
            self.TraverseNode = theNode

    def buildCommandParsingTree(self, theFunc):
        """Build the command parsing tree using the command arguments and the
        command syntax.

        Args:
            theFunc (function): command function.

        Returns:
            boolean: True if syntax tree is created, None else.
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
        raise CliException(MODULE, "Building Command Parsing Tree: arguments not defined")

    def getCmdAndCliArgos(self, theFunc, theInst, theLine):
        """Retrieve the command arguments stored in the command function and
        provided by @argo and @argos decorators; and the arguments passed by
        the user in the command line.

        Args:
            theFunc (function) : command function.
            theInst (object) : instance for the command function.
            theLine (str) : string with the command line input.

            Returns:
                tuple: pair with command arguments and cli arguments.
        """
        cmdArgos = getattr(theFunc, ARGOS_ATTR, None)
        if cmdArgos is None:
            return theFunc(theInst, theLine)
        cmdArgos.index()
        cliArgos = shlex.split(theLine)
        return cmdArgos, cliArgos

    def mapPassedArgosToCommandArgos(self, theRoot, theCmdArgos, theCliArgos):
        """Using the command arguments and argument values passed by the user
        in the CLI, map those using the command parsing tree in order to generate
        all arguments to be passed to the command function.

        Args:
            theRoot (node): node where mapping should starts.
            theCmdArgos (list): list with command arguments.
            theClidArgos (list): list with CLI arguments.
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
            raise CliException(MODULE, "Path for arguments {} not found.".format(theCliArgos))

    def buildCommandArgumentsFromSyntax(self, theFunc, theInst, theLine):
        """Method that build arguments to be passed to the command function.

        Args:
            theFunc (function) : command function.
            theInst (object) : instance for the command function.
            theLine (str) : string with the command line input.

        Returns:
            list: list with argument to be passed to the command function.
        """
        cmdArgos, cliArgos = self.getCmdAndCliArgos(theFunc, theInst, theLine)

        root = getattr(theFunc, TREE_ATTR, None)
        rules = getattr(theFunc, RULES_ATTR, None)
        if len(cliArgos) < RuleHandler.syntaxMinArgs(rules):
            raise CliException(MODULE, "Number of Args: Too few arguments")

        useArgs = self.mapPassedArgosToCommandArgos(root, cmdArgos, cliArgos)
        if useArgs is None:
            raise CliException(MODULE, 'Incorrect arguments"')
        if not all(map(lambda x: x is not None, useArgs)):
            raise CliException(MODULE, 'Mandatory argument is not present"')

        return useArgs


if __name__ == '__main__':
    pass
