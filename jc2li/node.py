__docformat__ = 'restructuredtext en'

# -----------------------------------------------------------------------------
#  _                            _
# (_)_ __ ___  _ __   ___  _ __| |_ ___
# | | '_ ` _ \| '_ \ / _ \| '__| __/ __|
# | | | | | | | |_) | (_) | |  | |_\__ \
# |_|_| |_| |_| .__/ \___/|_|   \__|___/
#             |_|
# -----------------------------------------------------------------------------
#
from jc2li.rules import RuleHandler as RH
from jc2li.clierror import CliException
from jc2li.argtypes import Prefix
import jc2li.loggerator as loggerator


# -----------------------------------------------------------------------------
#
#   ___ ___  _ __  ___| |_ __ _ _ __ | |_ ___
#  / __/ _ \| '_ \/ __| __/ _` | '_ \| __/ __|
# | (_| (_) | | | \__ \ || (_| | | | | |_\__ \
#  \___\___/|_| |_|___/\__\__,_|_| |_|\__|___/
#
# -----------------------------------------------------------------------------
#
MODULE = 'CLI.node'
logger = loggerator.getLoggerator(MODULE)


# -----------------------------------------------------------------------------
#       _                     _       __ _       _ _   _
#   ___| | __ _ ___ ___    __| | ___ / _(_)_ __ (_) |_(_) ___  _ __  ___
#  / __| |/ _` / __/ __|  / _` |/ _ \ |_| | '_ \| | __| |/ _ \| '_ \/ __|
# | (__| | (_| \__ \__ \ | (_| |  __/  _| | | | | | |_| | (_) | | | \__ \
#  \___|_|\__,_|___/___/  \__,_|\___|_| |_|_| |_|_|\__|_|\___/|_| |_|___/
#
# -----------------------------------------------------------------------------
#
class Node(object):
    """Node class provides a container for every node in the syntax tree.
    """

    def __init__(self, argo, **kwargs):
        """Node class initialization method.

        Args:
            argo (Argument): argument instance.
            parent (Node): parent node instance.
            label (str): string to be used as label attribute.
        """
        self._parent = kwargs.get('parent', None)
        self.children = list()
        self.argo = argo
        self.completer = argo.completer if argo else None
        self.browsable = True
        self.label = kwargs.get('label', self.name)
        self.__loops = set()
        self.__iscte = kwargs.get('iscte', False)

    @property
    def parent(self):
        """Get property that returns _parent attribute.

        Returns:
            Node: parent node instance in the syntax tree.
        """
        return self._parent

    @parent.setter
    def parent(self, parent):
        """Set property that sets a new parent for the node.

        Args:
            parent (Node): node instance to use a a new parent.
        """
        self._parent = parent

    @property
    def parents(self):
        """Get property that returns _parents attribute.

        Returns:
            :any:`list`: list with all parents for the node.
        """
        raise CliException(MODULE, 'parents() operation not allowed.')

    @property
    def argnode(self):
        return [self, ]

    def get_children_nodes(self, **kwargs):
        children = []
        noloop = kwargs.pop('matched') if kwargs.get('noloop', None) else False
        for child in self.traverse_children(noloop=noloop):
            children.extend(child.argnode)
        return children

    @property
    def siblings(self):
        """Get property that returns a list with all sibling nodes.

        Returns:
            :any:`list`: list with all Nodes that are sibling in the syntax tree.
        """
        if self.parent and self.parent.has_children():
            return self.parent.children
        else:
            return list()

    @property
    def name(self):
        """Get property that returns node name.

        Returns:
            str: string with the argument name.
        """
        return self.argo.name if self.argo else None

    @property
    def argtype(self):
        """Get property that returns node type.

        Returns:
            type: type for the argument contained in the node.
        """
        return self.argo.type if self.argo else None

    @property
    def default(self):
        """Get property that returns node default value.

        Returns:
            object: default value for the argument in the node.
        """
        return self.argo.default if self.argo else None

    @property
    def ancestor(self):
        """Get property that returns the node ancestor (parent).

        Returns:
            Node: node parent instance.
        """
        return self.parent

    @property
    def ancestors(self):
        """Get property that returns a list with all ancestors.

        Returns:
            list: list with all ancestors, parent of parent of ...
        """
        all_ancestors = list()
        traverse = self.parent
        while traverse:
            all_ancestors.append(traverse)
            traverse = traverse.ancestor
        return all_ancestors

    def _add_child(self, child, isloop=False):
        """Internal method that adds a new child Node to the Node.

        Args:
            child (Node): node to be added as a child.
            isloop (bool): True if child in a loop path.

        Returns:
            None
        """
        self.children.append(child)
        child.parent = self
        if isloop:
            self.__loops.add(child)

    def add_child(self, child, isloop=False):
        """Method that adds a new child Node to the Node.

        Args:
            child (Node): node to be added as a child.
            isloop (bool): True if child in a loop path.

        Returns:
            None
        """
        if child.parent and child.parent != self:
            raise CliException(MODULE, 'add_child() not allowed on child with parent.')
        else:
            self._add_child(child, isloop)

    def childrenNames(self):
        """Method that returns a list with the name for all children.

        Returns:
            list: list with all children names.
        """
        return [child.name for child in self.traverse_children()]

    def children_types(self):
        """Method that returns a list with the type for all children.

        Returns:
            list: list with all children types.
        """
        return [child.argtype for child in self.traverse_children()]

    def is_root(self):
        """Method that returns if the Node is the root node.

        Returns:
            bool: True if the node is the root node, False else.
        """
        return self.parent is None

    def has_children(self):
        """Method that returns if the node has children.

        Returns:
            int: numnber of children for node.
        """
        return len(self.children) > 0

    def has_siblings(self):
        """Method that returns in the node has siblings in the syntax tree.

        Returns:
            int: number of siblings for the node.
        """
        return self.parent and self.parent.has_children()

    def traverse_children(self, noloop=False):
        """Method that traverse all node children.

        Args:
            noloop (bool): True will avoid any child that is a loop path.

        Returns:
            generator: it returns a generator to be used in an iterator.
        """
        children = self.children if not noloop else [x for x in self.children if not self.isloop_child(x)]
        for child in children:
            yield child

    def traverse_siblings(self):
        """Method that traverse all siblings

        Returns:
            generator: it returns a generator to be used in an iterator.
        """
        for sibling in self.siblings:
            yield sibling

    def traverse_ancestors(self):
        """Method that traverse all ancestors.

        Returns:
            generator: it returns a generator to be used in an iterator.
        """
        for ancestor in self.ancestors:
            yield ancestor

    def find_by_name(self, name, **kwargs):
        """Method that checks if the node has the given name

        When looking for nodes in a path from the arguments passed in the
        command line, required arguments don't use the argument name, just
        the value, when looking for those in the parsing tree, they will not
        be found, but such as a mandatory and positional arguments, they
        should be a direct match for the direct position, that is the reason
        we use the argument check_default=True when we want to make a path
        search, for any other scenario, where just the argument name will be
        used, set that argument to False.

        Args:
            name (str): string with the node name.
            check_default (bool): if True validates the node if it has a\
                    valid default attribute (not None).

        Returns:
            Node: Node with the given name, None is not found.
        """
        node = None
        # if the node contains a constant, it has to be checked first and it
        # only should return a match, if the string passed is equal to the name
        # stored in the Node.
        if self.__iscte and self.name == name:
            node = self if self.name == name else None

        # Mandatory arguments have a default value equal to None, and they are
        # tested with check_default flag is set to True
        elif kwargs.get('check_default', None) and self.default is None:
            node = self

        # for any other parameter, checks the given name is the right one for a
        # proper match.
        else:
            node = self if self.name == name else None

        return node

    def find_child_by_name(self, name, **kwargs):
        """Method that returns the children node with the given name.

        Args:
            name (str): string with the node name.

        Returns:
            :any:`None`
        """
        for child in self.traverse_children():
            found_node = child.find_by_name(name, **kwargs)
            if found_node is not None:
                return found_node
        return None

    def is_any_child_browsable(self):
        """Method that returns if the node has any children that is
        browsable.

        Returns:
            bool: True if there is any browsable child, False else.
        """
        for child in self.traverse_children():
            if child.browsable:
                return True
        return False

    def isloop(self):
        """Method that returns if the node is a loop node.

        Returns:
            bool: True if it is a loop node, False else.
        """
        return False

    def isloop_child(self, child):
        """Method that returns if the node has any child that is a loop.

        Returns:
            bool: True if the node has loop child, False else.
        """
        return child in self.__loops

    def map_arg_to_value(self, value):
        """Maps the CLI argument entered to the value to be passed to the
        cli commana callback for the given node.

        Args:
            value (str) : String with the value entered by the user.

        Returns:
            str : String mapped for the given node.
        """
        if '=' in value:
            _, arg_value = value.split('=')
        else:
            arg_value = value
        arg_value = self.argo.type._(arg_value)
        return arg_value

    def store_value_in_argo(self, value, matched=False):
        """Stores a value in the argument for the node.

        Args:
            value (object) : Value to store in the argument.

            matched (bool) : True is argument was already matched and found\
                    in the command line entry.

        Returns:
            None
        """
        self.argo.completer.store(value, matched)

    def find_path(self, path_patterns):
        """Method that given a list of strings, finds a path in the syntax
        tree.

        The list of strings is the command line input, and it contains all
        argument values for a given command, which syntax is used as the
        syntax tree.

        The Argorithm traverse the syntax tree matching every argument and
        returning the Node that contains every argument, if it is found.

        Args:
            path_patterns (list): list with the command line input.

        Returns:
            list: list with Node for every argument found in the input pattern.
        """
        node_path = []
        trav = self
        for pattern in path_patterns:
            if '=' in pattern:
                name, _ = pattern.split("=")
                check_default = False
            else:
                check_default = True
                name = pattern
            trav = trav.find_child_by_name(name, check_default=check_default)
            if trav is None:
                raise CliException(MODULE, '<{}> not found'.format(pattern))
            else:
                node_path.append(trav)
        return node_path

    def build_children_node_from_rule(self, rule, argos):
        """Method that returns a child node under the given node for the
        given rule.

        child is the Node that has to be added inmidiatly.
        end_child is the Node that has to be returned as the next node in the
        sequence. For OnlyOneRule or endDrule it does not matter, because it
        the same node, but for any other rule that includes Hook, child will
        be the first/start hook, and next child will be last/end hook.

        Args:
            rule (dict): dictionay with a syntax rule.
            argos (Arguments): command Arguments instance.

        Returns:
            Node: child node that matches the syntax rule.
        """
        args_from_rule = RH.get_args_from_rule(rule)
        if isinstance(args_from_rule, str):
            argo_from_name = argos.get_argo_from_name(args_from_rule)

        if RH.is_end_rule(rule):
            child = End(parent=self)
            end_child = child

        elif RH.is_only_one_rule(rule):
            child = FreeformNode(argo_from_name, parent=self)
            end_child = child

        elif RH.is_constant_rule(rule):
            child = CteNode(argo_from_name, parent=self)
            end_child = child

        elif RH.is_free_form_param_rule(rule):
            child = FreeformNode(argo_from_name, parent=self)
            end_child = child

        elif RH.is_cte_param_rule(rule):
            child = PrefixNode(argo_from_name, parent=self)
            end_child = FreeformNode(argo_from_name)
            child.add_child(end_child)

        elif RH.is_zero_or_one_rule(rule) or RH.is_only_one_option_rule(rule):
            child = Hook(parent=self, label="Hook-Start")
            end_child = Hook(label="Hook-End")
            end_child = child.build_hook_from_rule(args_from_rule, argos, end_child)
            if RH.is_zero_or_one_rule(rule):
                child.add_child(end_child)

        elif RH.is_zero_or_more_rule(rule) or\
                RH.is_one_or_more_rule(rule) or\
                RH.is_free_form_rule(rule):
            child = Hook(parent=self, label="Hook-Start")
            loop_child = Loop(parent=self, label="Hook-Loop")
            end_child = Hook(parent=self, label="Hook-End")
            loop_child = child.build_hook_from_rule(args_from_rule, argos, loop_child)
            loop_child.add_child(end_child)
            loop_child.add_child(child, isloop=True)
            if RH.is_zero_or_more_rule(rule):
                child.add_child(end_child)

        else:
            raise CliException(MODULE, 'Unkown type of rule.')

        self.add_child(child)
        return end_child

    def find_nodes(self):
        """Method that returns all nodes to be traversed.

        Returns:
            list: list with all nodes to be traversed underneath the given node.
        """
        nodes = [self, ]
        for child in self.traverse_children():
            nodes += child.find_nodes()
        return nodes

    def _to_string(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}Node.{}\n".format(indent, self.label)

    def to_str(self, level):
        """Method that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        st = self._to_string(level)
        for child in self.traverse_children(noloop=True):
            st += child.to_str(level + 1)
        return st

    def __str__(self):
        """Method that returns the string to be used when converting the
        instance to string.

        Returns:
            str: string with node information.
        """
        return self.to_str(0)


# -----------------------------------------------------------------------------
#
class CteNode(Node):
    """CteNode class derives from Node and it  provides a container
    for every node that can contain a constant.
    """

    def find_by_name(self, name, **kwargs):
        """Method that checks if the node has the given name

        When looking for nodes in a path from the arguments passed in the
        command line, required arguments don't use the argument name, just
        the value, when looking for those in the parsing tree, they will not
        be found, but such as a mandatory and positional arguments, they
        should be a direct match for the direct position, that is the reason
        we use the argument check_default=True when we want to make a path
        search, for any other scenario, where just the argument name will be
        used, set that argument to False.

        Args:
            name (str): string with the node name.
            check_default (bool): if True validates the node if it has a\
                    valid default attribute (not None).

        Returns:
            Node: Node with the given name, None is not found.
        """
        return self if self.name == name else None


# -----------------------------------------------------------------------------
#
class PrefixNode(Node):
    """PrefixNode class derives from Node and it provides a container for
    any node that keeps a prefix for a parameter.
    """

    def __init__(self, argo, **kwargs):
        """PrefixNode class initialization method.

        Args:
            parent (Node): parent node instance.
            label (str): string to be used as label attribute.
        """
        super(PrefixNode, self).__init__(None, **kwargs)
        self.label = kwargs.get('label', argo.name)
        self.completer = Prefix(label=self.label)

    def find_by_name(self, name, **kwargs):
        """Method that checks if the node has the given name

        When looking for nodes in a path from the arguments passed in the
        command line, required arguments don't use the argument name, just
        the value, when looking for those in the parsing tree, they will not
        be found, but such as a mandatory and positional arguments, they
        should be a direct match for the direct position, that is the reason
        we use the argument check_default=True when we want to make a path
        search, for any other scenario, where just the argument name will be
        used, set that argument to False.

        Args:
            name (str): string with the node name.
            check_default (bool): if True validates the node if it has a\
                    valid default attribute (not None).

        Returns:
            Node: Node with the given name, None is not found.
        """
        if name.startswith('-') and name[1:] == self.label:
            return self
        return None

    def map_arg_to_value(self, value):
        """Maps the CLI argument entered to the value to be passed to the
        cli commana callback for the given node.

        Args:
            value (str) : String with the value entered by the user.

        Returns:
            str : String mapped for the given node.
        """
        if value.startswith('-'):
            arg_value = value[1:]
        else:
            raise NotImplementedError
        arg_value = str(arg_value)
        return arg_value

    def store_value_in_argo(self, value, matched=False):
        """Stores a value in the argument for the node.

        Args:
            value (object) : Value to store in the argument.

            matched (bool) : True is argument was already matched and found\
                    in the command line entry.

        Returns:
            None
        """
        pass


# -----------------------------------------------------------------------------
#
class FreeformNode(Node):
    """FreeformNode class derives from Node and it  provides a container
    for every node that can contain any kind of information.
    """

    def map_arg_to_value(self, value):
        """Maps the CLI argument entered to the value to be passed to the
        cli commana callback for the given node.

        Args:
            value (str) : String with the value entered by the user.

        Returns:
            str : String mapped for the given node.
        """
        value = self.argo.type._(value)
        return value

    def find_by_name(self, name, **kwargs):
        """Method that checks if the node has the given name

        When looking for nodes in a path from the arguments passed in the
        command line, required arguments don't use the argument name, just
        the value, when looking for those in the parsing tree, they will not
        be found, but such as a mandatory and positional arguments, they
        should be a direct match for the direct position, that is the reason
        we use the argument check_default=True when we want to make a path
        search, for any other scenario, where just the argument name will be
        used, set that argument to False.

        Args:
            name (str): string with the node name.
            check_default (bool): if True validates the node if it has a\
                    valid default attribute (not None).

        Returns:
            Node: Node with the given name, None is not found.
        """
        return self


# -----------------------------------------------------------------------------
#
class Hook(Node):
    """Hook class provides a container for every node that not contains any
    argument information but is used to provides different branches in the
    syntax tree.
    """

    def __init__(self, **kwargs):
        """Hook class initialization method.

        Args:
            parent (Node): parent node instance.
            label (str): string to be used as label attribute.
        """
        super(Hook, self).__init__(None, **kwargs)
        self.browsable = False
        if kwargs.get('parent', None) is None:
            self._parent = []
        else:
            self._parent = [self._parent, ]
        self.label = kwargs.get('label', "Hook")

    @property
    def parent(self):
        """Get property that returns _parent attribute.

        Returns:
            Node: parent node instance in the syntax tree.
        """
        return None

    @parent.setter
    def parent(self, parent):
        """Set property that sets a new parent for the node.

        Args:
            parent (Node): node instance to use a a new parent.
        """
        self._parent.append(parent)

    @property
    def ancestor(self):
        """Get property that returns the node ancestor (parent).

        Returns:
            Node: node parent instance.
        """
        return None

    @property
    def parents(self):
        """Get property that returns _parents attribute.

        Returns:
            list: list with all parents for the node.
        """
        return self._parent

    @property
    def name(self):
        """Get property that returns node name.

        Returns:
            str: string with the argument name.
        """
        return None

    @property
    def argtype(self):
        """Get property that returns node type.

        Returns:
            type: type for the argument contained in the node.
        """
        return None

    @property
    def default(self):
        """Get property that returns node default value.

        Returns:
            object: default value for the argument in the node.
        """
        return None

    @property
    def argnode(self):
        return self.get_children_nodes()

    def add_child(self, child, isloop=False):
        """Method that adds a new child Node to the Node.

        Args:
            child (Node): node to be added as a child.
            isloop (bool): True if child in a loop path.

        Returns:
            None
        """
        self._add_child(child, isloop)

    def find_by_name(self, name, **kwargs):
        """Method that checks if the node has the given name

        When looking for nodes in a path from the arguments passed in the
        command line, required arguments don't use the argument name, just
        the value, when looking for those in the parsing tree, they will not
        be found, but such as a mandatory and positional arguments, they
        should be a direct match for the direct position, that is the reason
        whe use the argument check_default=True when we want to make a path
        search, for any other scenario, where just the argument name will be
        used, set that argument to False.

        Args:
            name (str): string with the node name.
            check_default (bool): if True validates the node if it has a\
                    valid default attribute (not None).

        Returns:
            Node: Node with the given name, None is not found.
        """
        return self.find_child_by_name(name, **kwargs)

    def build_hook_from_rule(self, rule, argos, end_hook):
        """Method that build a sequence of nodes for the given rule.

        Args:
            rule (dict): dictionary with the rule to use.
            argos (Arguments): command Argumets instance.
            end_hook (Node): node that will be the last node.

        Returns:
            Node: Last node for the sequence being created.
        """
        def _add_grant_child(child, grant_child):
            if child:
                child.add_child(grant_child)

        if type(rule) in [list, dict]:
            child = None
            grant_child = None
            # Every rule can be visited only one time
            for rule in rule:
                if RH.is_end_rule(rule):
                    raise TypeError('Error : Hook : endpoint not allowed in rule')
                if RH.get_counter_from_rule(rule) == 0:
                    _add_grant_child(child, end_hook)
                    child = self.build_children_node_from_rule(rule, argos)
                else:
                    grant_child = child.build_children_node_from_rule(rule, argos)
                    # This is not required because it is done in
                    # build_children_node_from_rule call.:update
                    # child.add_child(grant_child)
                    child = grant_child
            _add_grant_child(child, end_hook)
            return end_hook
        else:
            raise TypeError('Error: Hook : node requires a list of rules')

    def find_nodes(self):
        """Method that returns all nodes to be traversed.

        Returns:
            list: list with all nodes to be traversed underneath the given
            node.
        """
        nodes = list()
        for child in self.traverse_children():
            nodes += child.find_nodes()
        return nodes

    def _to_string(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}Hook.{}\n".format(indent, self.label)


# -----------------------------------------------------------------------------
#
class Loop(Hook):
    """Loop class provides a container for every node that not contains any
    argument information but is used to provides different loops in the
    syntax tree.
    """

    def __init__(self, **kwargs):
        """Loop class initialization method.

        Args:
            parent (Node): parent node instance.
            label (str): string to be used as label attribute.
        """
        super(Loop, self).__init__(**kwargs)
        self.label = kwargs.get('label', "Loop")

    def isloop(self):
        """Method that returns if the node is a loop node.

        Returns:
            bool: True if it is a loop node, False else.
        """
        return True

    def _to_string(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}Loop.{}\n".format(indent, self.label)

    def get_children_nodes(self, **kwargs):
        if kwargs.get('matched', None):
            kwargs.pop('matched')
            kwargs.setdefault('noloop', True)
        else:
            kwargs.setdefault('matched', True)
            kwargs.setdefault('noloop', False)
        return super(Loop, self).get_children_nodes(**kwargs)

    def find_child_by_name(self, name, **kwargs):
        """Method that returns the children node with the given name.

        Args:
            name (str): string with the node name.
            matched (bool): True if the node was already traverse,\
                    False else.
        """
        if kwargs.get('matched', None):
            kwargs.pop('matched')
            noLoop = True
        else:
            kwargs.setdefault('matched', True)
            noLoop = False
        for child in self.traverse_children(noloop=noLoop):
            found_node = child.find_by_name(name, **kwargs)
            if found_node is not None:
                return found_node
        return None


# -----------------------------------------------------------------------------
#
class Start(Hook):
    """Start class provides a container for every node that not contains any
    argument information but is used to provides the root node fo the syntax
    tree.
    """

    def __init__(self, **kwargs):
        """Start class initialization method.

        Args:
            parent (Node): parent node instance.
            label (str): string to be used as label attribute.
        """
        super(Start, self).__init__(**kwargs)
        self.label = kwargs.get('label', "Start")

    def _to_string(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}Start.{}\n".format(indent, self.label)


# -----------------------------------------------------------------------------
#
class End(Hook):
    """Start class provides a container for every node that not contains any
    argument information but is used to provides the last node fo the syntax
    tree.
    """

    def __init__(self, **kwargs):
        """End class initialization method.

        Args:
            parent (Node): parent node instance.
            label (str): string to be used as label attribute.
        """
        """
        """
        super(End, self).__init__(**kwargs)
        self.label = kwargs.get('label', "End")

    def build_hook_from_rule(self, rule, argos, end_hook):
        """Method that build a sequence of nodes for the given rule.

        Args:
            rule (dict): dictionary with the rule to use.
            argos (Arguments): command Argumets instance.
            end_hook (Node): node that will be the last node.

        Returns:
            Node: Last node for the sequence being created.
        """
        raise TypeError('Error: End : can not build nodes after end')

    def _to_string(self, level):
        """Internal ethod that returns a string with Node information.

        Args:
            level (int): indentation level for the Node.

        Returns:
            str: string with node information.
        """
        indent = "--" * level
        return "{}End.{}\n".format(indent, self.label)
