import shlex
from rules import RuleHandler
from common import ARGOS_ATTR, RULES_ATTR, TREE_ATTR
from node import Start
from clierror import CliException
import loggerator

MODULE = 'JOURNAL'


logger = loggerator.getLoggerator('journal')


class Journal(object):
    """Journal class that provides a container with all matching required for
    checking if the commmand syntax is valid and napping arguments entered in
    the command line with command arguments.
    """

    def __init__(self):
        """Journal class initialization method.
        """
        self.path = list()
        self.argos = dict()
        self.traverse_node = None
        self.root = None
        self.__cache = {}

    def get_from_cache(self, key):
        """Retreives some data to the cache.

        Args:
            key (object) : key for the cached data to be retrieved.

        Returns:
            object : data found in cache, None if key is not found.
        """
        return self.__cache.get(key, None)

    def set_to_cache(self, key, value):
        """Adds cache data for the given key.

        If the key already exits, the data is being overwritten.

        Args:
            key (object) : key for the data to be cached.
            value (object) : data being cached.
        """
        self.__cache[key] = value

    def add_node(self, node):
        """Method that adds a new node.

        Args:
            node (Node): node instance to be added.
        """
        if node:
            self.path.append(node)
            self.argos.update(node.argo)
            self.traverse_node = node

    def build_command_parsing_tree(self, f):
        """Build the command parsing tree using the command arguments and the
        command syntax.

        Args:
            f (function): command function.

        Returns:
            boolean: True if syntax tree is created, None else.
        """
        root = Start()
        argos = getattr(f, ARGOS_ATTR, None)
        if argos:
            argos.index()
            rules = getattr(f, RULES_ATTR, list())
            trav = root
            for rule in rules:
                new_trav = trav.build_children_node_from_rule(rule, argos)
                trav = new_trav
            setattr(f, TREE_ATTR, root)
            return root
        raise CliException(MODULE, "Building Command Parsing Tree: arguments not defined")

    def get_cmd_and_cli_args(self, f, instance, line):
        """Retrieve the command arguments stored in the command function and
        provided by @argo and @argos decorators; and the arguments passed by
        the user in the command line.

        Args:
            f (function) : command function.
            instance (object) : instance for the command function.
            line (str) : string with the command line input.

            Returns:
                tuple: pair with command arguments and cli arguments.
        """
        cmd_argos = getattr(f, ARGOS_ATTR, None)
        if instance and cmd_argos is None:
            return f(instance, line)
        elif cmd_argos is not None:
            cmd_argos.index()
            try:
                if line.count('"') % 2 == 1:
                    line = line.replace('"', '*')
                cli_args = shlex.split(line)
                return cmd_argos, cli_args
            except ValueError:
                return None, None
        return None, None

    def map_passed_args_to_command_argos(self, root, cmd_argos, cli_args):
        """Using the command arguments and argument values passed by the user
        in the CLI, map those using the command parsing tree in order to generate
        all arguments to be passed to the command function.

        Args:
            root (node): node where mapping should starts.
            cmd_argos (list): list with command arguments.
            cli_args (list): list with CLI arguments.
        """
        node_path = root.find_path(cli_args)
        matched_nodes = list()
        for node, val in zip(node_path, cli_args):
            if '=' in val:
                _, arg_value = val.split('=')
            else:
                arg_value = val
            arg_value = node.argo.type._(arg_value)
            if node not in matched_nodes:
                node.argo.value = arg_value
            else:
                if type(node.argo.value) == list:
                    node.argo.value.append(arg_value)
                else:
                    node.argo.value = [node.argo.value, arg_value]
            matched_nodes.append(node)
        use_args = cmd_argos.get_indexed_values()
        return use_args

    def build_command_arguments_from_syntax(self, f, instance, line):
        """Method that build arguments to be passed to the command function.

        Args:
            f (function) : command function.
            instance (object) : instance for the command function.
            line (str) : string with the command line input.

        Returns:
            list: list with argument to be passed to the command function.
        """
        cmd_argos, cli_args = self.get_cmd_and_cli_args(f, instance, line)

        root = getattr(f, TREE_ATTR, None)
        rules = getattr(f, RULES_ATTR, None)
        if len(cli_args) < RuleHandler.syntax_min_args(rules):
            raise CliException(MODULE, "Number of Args: Too few arguments")

        use_args = self.map_passed_args_to_command_argos(root, cmd_argos, cli_args)
        if use_args is None:
            raise CliException(MODULE, 'Incorrect arguments"')
        if not all(map(lambda x: x is not None, use_args)):
            raise CliException(MODULE, 'Mandatory argument is not present')

        return use_args

    def build_command_arguments_from_args(self, f, line):
        """Method that build arguments to be passed to the command function.

        Args:
            f (function) : command function.
            line (str) : string with the command line input.

        Returns:
            list: pair with the list with argument to be passed to the\
                    command function and remaining entries in the command\
                    line.
        """
        cmd_argos = getattr(f, ARGOS_ATTR, None)
        if cmd_argos:
            cmd_argos.index()
            cli_args = shlex.split(line)
            cli_args.reverse()
            for arg in cmd_argos.traverse():
                arg.value = arg.type._(cli_args.pop())
            use_args = cmd_argos.get_indexed_values()
            if all(map(lambda x: x is not None, use_args)):
                return use_args, cli_args
            else:
                raise NotImplementedError('Mandatory argument is not present')
        else:
            raise NotImplementedError('Command with SYNTAX without ARGOS')
