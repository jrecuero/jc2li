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
# from __future__ import unicode_literals
from functools import wraps, partial
import sys
import inspect
import json
# import shlex
import jc2li.loggerator as loggerator
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
# from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.token import Token
from prompt_toolkit.styles import style_from_dict
from jc2li.common import TREE_ATTR, SYNTAX_ATTR, ARGOS_ATTR
from jc2li.journal import Journal


# -----------------------------------------------------------------------------
#
#   ___ ___  _ __  ___| |_ __ _ _ __ | |_ ___
#  / __/ _ \| '_ \/ __| __/ _` | '_ \| __/ __|
# | (_| (_) | | | \__ \ || (_| | | | | |_\__ \
#  \___\___/|_| |_|___/\__\__,_|_| |_|\__|___/
#
# -----------------------------------------------------------------------------
#
MODULE = 'CLI.base'
LOGGER = loggerator.getLoggerator(MODULE)


# -----------------------------------------------------------------------------
#       _                     _       __ _       _ _   _
#   ___| | __ _ ___ ___    __| | ___ / _(_)_ __ (_) |_(_) ___  _ __  ___
#  / __| |/ _` / __/ __|  / _` |/ _ \ |_| | '_ \| | __| |/ _ \| '_ \/ __|
# | (__| | (_| \__ \__ \ | (_| |  __/  _| | | | | | |_| | (_) | | | \__ \
#  \___|_|\__,_|___/___/  \__,_|\___|_| |_|_| |_|_|\__|_|\___/|_| |_|___/
#
# -----------------------------------------------------------------------------
#
class CliBase(object):
    """CliBase class is the base class for any class that will implement
    commands to be used by the command line interface.

    Attributes:
        _WALL (:any:`dict`) : Internal dictionary used to update commands defined\
                in derived classes.

        CLI_STYLE (:any:`dict`) : Dictionary with default styles to be used in the\
                command line.
    """

    _WALL = {}
    CLI_STYLE = style_from_dict({Token.Toolbar: '#ffffff italic bg:#007777',
                                 Token.RPrompt: 'bg:#ff0066 #ffffff', })
    __MODES = []

    class CliCompleter(Completer):
        """CliCompleter class provide completion to any entry in the command line.

        This class should make use of every completer for command arguments.
        """

        def __init__(self, cli):
            """CliCompleter initialization method.

            Args:
                cli (CliBase) : Cli instance.
            """
            self._nodepath = None
            self._cli = cli

        def get_completions(self, document, complete_event):
            """Method that provides completion for any input in the command line.

            Args:
                document (:class:`Document`) : Document instance with command line input data.
                compleEvent (:class:`CompleteEvent`) : Event with iinput information

            Returns:
                :class:`Completion` : Completion instance with data to be completed.
            """
            # self._nodepath = None
            word_before_cursor = document.get_word_before_cursor(WORD=True)
            if ' ' not in document.text:
                matches = [m for m in self._cli.commands if m.startswith(word_before_cursor)]
                for m in matches:
                    yield Completion(m, start_position=-len(word_before_cursor))
            else:
                line_as_list = document.text.split()
                if len(line_as_list) == 0:
                    return
                last_token = line_as_list[-1] if document.text[-1] != ' ' else ' '
                cmdlabel = line_as_list[0]
                command = self._cli.get_command_cb(cmdlabel)
                if command is not None:
                    # Required for partial methods
                    if hasattr(command, 'func'):
                        command = command.func
                    root = getattr(command, TREE_ATTR, None)
                    journal = self._cli.journal
                    _, cli_argos = journal.get_cmd_and_cli_args(command, None, " ".join(line_as_list[1:]))
                    nodepath = None
                    children_nodes = None
                    try:
                        nodepath = root.find_path(cli_argos)
                    except Exception as ex:
                        LOGGER.error('{0}, {1} | {2}'.format(ex, ex.__traceback__.tb_lineno, self._nodepath))

                    if not nodepath and self._nodepath is None:
                        # if there is not path being found and there is not any
                        # previous path, just get the completion under the root.
                        self._nodepath = [root, ]
                    elif nodepath and document.text[-1] == ' ':
                        # if there is a path found and the last character
                        # entered is a space, use that path.
                        self._nodepath = nodepath

                    if self._nodepath:
                        # Get children from the path found or the the last path
                        children_nodes = self._nodepath[-1].get_children_nodes() if self._nodepath[-1] else None
                    else:
                        # if there was not path or any last path, get children
                        # from the root.
                        children_nodes = root.get_children_nodes()

                    if children_nodes:
                        helps = [c.completer.help(last_token) for c in children_nodes]
                        self._cli.toolbar_str = " | ".join(helps)
                        for child in children_nodes:
                            LOGGER.debug('child is: {0}'.format(child.label))
                            matches = child.completer.complete(document, last_token)
                            if matches is None:
                                continue
                            for i, m in enumerate(matches):
                                yield Completion(m, start_position=-len(word_before_cursor))
                                # TODO: Remove help displayed in the completer
                                # yield Completion(m, start_position=-len(word_before_cursor), display_meta=helps[i])
                    # TODO: Trace and debug information to be removed or optimized.
                    LOGGER.debug('completer command: {0}'.format(command))
                    LOGGER.debug('document text is "{}"'.format(document.text))
                    LOGGER.debug('last document text is [{}]'.format(line_as_list[-1]))
                    LOGGER.debug('children nodes are {}'.format(children_nodes))
                    if children_nodes:
                        LOGGER.debug('children nodes are {}'.format([x.name for x in children_nodes]))
                    LOGGER.debug('nodepath is {}'.format(nodepath))
                    if nodepath:
                        LOGGER.debug('nodepath is {}'.format([x.name for x in nodepath]))
                    if self._nodepath and self._nodepath[-1] is not None:
                        LOGGER.debug('self._nodepath is {}'.format(self._nodepath))
                        LOGGER.debug('self._nodepath is {}'.format([x.name for x in self._nodepath]))

    def __init__(self):
        """CliBase class initialization method.
        """
        self.command = None
        self.last_cmd = None
        self.toolbar_str = ''
        self.rprompt_str = ''
        self.prompt_str = "> "
        self.__commands = {}
        self.journal = Journal()
        self.setup_commands()
        self.__recording = False
        self.__record_data = []

    @property
    def commands(self):
        """Get property that returns keys for _cmdDict attribute

        Returns:
            :any:`list` : List with all command labels.
        """
        return self.__commands.keys()

    @property
    def mode_stack(self):
        return CliBase.__MODES

    def get_command_cb(self, command):
        """Get the command callback for the given command label.

        Args:
            command (str) : String with the command label.

        Returns:
            :any:`function` : callback function for the given command.
        """
        command_entry = self.__commands.get(command, (None, None))
        return command_entry[0]

    def get_command_desc(self, command):
        """Get the command description for the given command label.

        Args:
            command (str) : String with the command label.

        Returns:
            str : description for the given command.
        """
        command_entry = self.__commands.get(command, (None, None))
        return command_entry[1]

    def is_command(self, command):
        """Returns if the given command label is found in the list of available
        commands.

        Args:
            command (str) : Command label to check as an availbale command.

        Returns:
            bool : True if command label is found, False else.
        """
        return command in self.commands

    def add_command(self, command, command_cb, desc=""):
        """Adds a new entry to the command dictionary.

        Args:
            command (str) : String with the command label.
            command_cb (:any:`function`) : Function with the command callback.

        Returns:
            bool : True if command was added.
        """
        if self.is_command(command):
            LOGGER.warning('[{}] Command [{}] already present.'.format(MODULE, command))
        self.__commands[command] = (command_cb, desc)

        # At this point, inject the context in every argument attributes using
        # command_cb.func._arguments._arguments[#].completer. That should work
        # only for those with _arguments attribute inside command_cb.func.
        if hasattr(command_cb, 'func') and hasattr(command_cb.func, ARGOS_ATTR):
            for argument in getattr(command_cb.func, ARGOS_ATTR).arguments:
                argument.journal = self.journal

        return True

    def exec_command(self, command, user_input):
        """Executes the command callback for the given command label.

        Args:
            command (str) : Command label for the command to execute.
            user_input (str) : String with the command line input.

        Returns:
            object : value returned by the command callback.
        """
        command_cb = self.get_command_cb(command)
        if command_cb:
            return command_cb(user_input)

    def empty_line(self):
        """Method that don't provide any action when <CR> is entered in an
        empty line.

        By default, the same command is executed when just <CR> is entered,
        but we don't want that behavior.

        Returns:
            :any:`None`
        """
        pass

    def precmd(self, command, line):
        """Method to be called before any command is being processed.

        Args:
            command (str) : String with new command entered.

            line (str): string entered in the command line.

        Returns:
            bool : False will skip command execution.
        """
        return True

    def onecmd(self, line):
        """Method to be called when any command is being processed.

        Args:
            line (str): string entered in the command line.

        Returns:
            bool : False will exit command loop.
        """
        return True

    def postcmd(self, command, line):
        """Method to be called after any command is being processed.

        Args:
            command (str) : String with new command entered.

            line (str): string entered in the command line.

        Returns:
            bool : False will exit command loop.
        """
        return True

    def get_bottom_toolbar_tokens(self, cli):
        """Method that provides data and format to be displayed in the ToolBar.

        Args:
            cli (:class:`CommandLineInterface`) : CommandLineInterface instance.

        Returns:
            :any:`list` : list with data to be displayed in the ToolBar.
        """
        return [(Token.Toolbar, '{}'.format(self.toolbar_str)), ]

    def get_rprompt_tokens(self, cli):
        """Returns tokens for command line right prompt.

        Args:
            cli (:class:`CommandLineInterface`) : CommandLineInterface instance.

        Returns:
            :any:`list` : list with data to be displayed in the right prompt..
        """
        return [(Token.RPrompt, '{}'.format(self.rprompt_str)), ]

    def get_prompt_tokens(self, cli):
        """Returns tokens for command line prompt.

        Args:
            cli (:class:`CommandLineInterface`) : CommandLineInterface instance.

        Returns:
            :any:`list` : list with data to be displayed in the prompt.
        """
        return [(Token.Prompt, '{}'.format(self.prompt_str)), ]

    def extend_commands_from_class(self, classname):
        """Extends commands defined in a class to be included in the full
        command line.

        This is required only for commands defined in a class that is being
        derived, and the derived class is the one being used in the command
        line. This method allows to include all commands from the base
        class.

        Args:
            classname (str) : String with class name for the class which\
                    methods should be imported.

        Returns:
            None
        """
        for name, func_cb, desc in self._WALL.get(classname, []):
            self.add_command(name, partial(func_cb, self), desc)

    def setup_commands(self):
        """Register all commands to be used by the command line interface.

        Returns:
            None
        """
        classname = self.__class__.__name__
        calls = self._WALL.get(classname, [])
        for name, func_cb, desc in calls:
            LOGGER.debug('{0}::setup_commands add command {1}::{2}'.format(classname, name, func_cb))
            self.add_command(name, partial(func_cb, self), desc)

    def run_prompt(self, **kwargs):
        """Execute the command line.

        Args:
            prompt (:any:`str` or :any:`function`) : string or callback with prompt value

            toolbar (:any:`str` or :any:`function`) : string or callback with toolbar value.

            rprompt (:any:`str` or :any:`function`) : string or callback with right prompt value.

        Returns:
            str : String with the input entered by the user.
        """
        toolbar = kwargs.get('toolbar', 'Enter a valid command')
        self.toolbar_str = toolbar if isinstance(toolbar, str) else toolbar()

        _prompt = kwargs.get('prompt', self.prompt_str)
        self.prompt_str = _prompt if isinstance(_prompt, str) else _prompt()

        rprompt = kwargs.get('rprompt', None)
        if rprompt is not None:
            self.rprompt_str = rprompt if isinstance(rprompt, str) else rprompt()

        user_input = prompt(history=FileHistory('history.txt'),
                            auto_suggest=AutoSuggestFromHistory(),
                            completer=CliBase.CliCompleter(self),
                            # lexer=SqlLexer,
                            get_bottom_toolbar_tokens=self.get_bottom_toolbar_tokens,
                            get_rprompt_tokens=self.get_rprompt_tokens,
                            get_prompt_tokens=self.get_prompt_tokens,
                            style=self.CLI_STYLE,
                            # validator=CliValidator(),
                            refresh_interval=1)
        return user_input

    def start_recording(self):
        """Starts recording commands input in the command line.

        Returns:
            None
        """
        self.__recording = True

    def stop_recording(self):
        """Stops recording commands input in the command line.

        Returns:
            None
        """
        self.__recording = False
        if self.__record_data:
            del self.__record_data[-1]

    def clear_recording(self, from_record=None, to_record=None):
        """Clears the range of records recorded from the given range.

        Args:
            from_record (int) : First record to clear. Set to 0 if None.

            to_record (int): Last record to clear. Set to last if None
        """
        if from_record is None and to_record is None:
            self.__record_data.clear()
        elif from_record is None and to_record is not None:
            if to_record < len(self.__record_data):
                del self.__record_data[:to_record + 1]
        elif from_record is not None and to_record is None:
            if 0 <= from_record <= len(self.__record_data):
                del self.__record_data[from_record:]
        elif (0 <= from_record <= len(self.__record_data)) and\
                to_record < len(self.__record_data) and\
                from_record <= to_record:
                del self.__record_data[from_record:to_record + 1]
        else:
            pass

    def select_recording(self, from_record=None, to_record=None):
        """Selects the range of records recorded from the given range.

        Args:
            from_record (int) : First record to select. Set to 0 if None.

            to_record (int): Last record to select. Set to last if None

        Returns:
            list : List of selected records.
        """
        if from_record is None and to_record is None:
            return self.__record_data
        elif from_record is None and to_record is not None:
            if to_record < len(self.__record_data):
                return self.__record_data[:to_record + 1]
        elif from_record is not None and to_record is None:
            if 0 <= from_record <= len(self.__record_data):
                return self.__record_data[from_record:]
        elif (0 <= from_record <= len(self.__record_data)) and\
                to_record < len(self.__record_data) and\
                from_record < to_record:
                return self.__record_data[from_record:to_record + 1]
        else:
            return []

    def display_recording(self, from_record=None, to_record=None):
        """Displays the range of records recorded from the given range.

        Args:
            from_record (int) : First record to display. Set to 0 if None.

            to_record (int): Last record to display. Set to last if None

        Returns:
            None
        """
        records = self.select_recording(from_record, to_record)
        for i, record in enumerate(records):
            LOGGER.display('{0}: {1}'.format(i, record))

    def save_recording(self, filename, from_record=None, to_record=None):
        """
        """
        records = self.select_recording(from_record, to_record)
        to_save = []
        for record in records:
            to_save.append({'command': record})
        if to_save:
            with open(filename, 'w') as f:
                json.dump(to_save, f)

    def record_command(self, user_input):
        """Saves in a JSON file the range of records recorded from the given
        range.

        Args:
            from_record (int) : First record to save. Set to 0 if None.

            to_record (int): Last record to save. Set to last if None

        Returns:
            None
        """
        if self.__recording:
            self.__record_data.append(user_input)

    def exec_user_input(self, user_input, **kwargs):
        """Executes the string with the user input.

        Args:
            user_input (str) : String with the input entered by the user.

        Keyword Args:
            precmd (bool) : True if precmd shoud be called.

            postcmd (bool) : True if postcmd should be called.

        Returns:
            bool : True if application shoudl continue, False else.
        """
        pre_return = True
        cb_return = True
        post_return = True
        if user_input:
            line_as_list = user_input.split()
            if len(line_as_list) == 0:
                return True
            command = line_as_list[0]
            if self.is_command(command):
                if kwargs.get('precmd', False):
                    pre_return = self.precmd(command, user_input)
                # precmd callback return value can be used to skip command
                # of it returns False.
                if pre_return:
                    self.record_command(user_input)
                    cb_return = self.exec_command(command, ' '.join(line_as_list[1:]))
                # postcmd callback return value can be used to exit the
                # command loop if it returns False..
                if kwargs.get('postcmd', False):
                    post_return = self.postcmd(command, user_input)
            self.last_cmd = user_input
        else:
            post_return = self.onecmd(user_input)
        return post_return if cb_return is not False else cb_return

    def cmdloop(self, **kwargs):
        """Method that is called to wait for any user input.

        Keyword Args:
            prompt (:any:`str` or :any:`function`) : string or callback with prompt value

            toolbar (:class:`str` or :any:`function`) : string or callback with toolbar value.

            rprompt (:any:`str` or :any:`function`) : string or callback with right prompt value.

            echo (bool) : True is command should be echoed.

            precmd (bool) : True if precmd shoud be called.

            postcmd (bool) : True if postcmd should be called.

        Returns:
            None
        """
        while True:
            user_input = self.run_prompt(**kwargs)
            if kwargs.get('echo', False):
                LOGGER.display(user_input)
            if not self.exec_user_input(user_input, **kwargs):
                return

    def run(self, **kwargs):
        """Runs the command line interface for the given cli class.

        Keyword Args:
            prompt (:any:`str` or :any:`function`) : string or callback with prompt value

            toolbar (:class:`str` or :any:`function`) : string or callback with toolbar value.

            rprompt (:any:`str` or :any:`function`) : string or callback with right prompt value.

            echo (bool) : True is command should be echoed.

            precmd (bool) : True if precmd shoud be called.

            postcmd (bool) : True if postcmd should be called.

        Returns:
            None
        """
        try:
            self.cmdloop(**kwargs)
        except KeyboardInterrupt:
            LOGGER.display("")
            pass

    def run_mode(self, **kwargs):
        """Enters in a new mode.

        In a new mode, parent commands are not available and the new scope
        is for commands defined in the created mode.

        Returns:
            None
        """
        mode_name = self.__class__.__name__
        CliBase.__MODES.append(mode_name)
        self.run(**kwargs)

    def leave_mode(self, **kwargs):
        """Exits the running mode.

        Returns:
            str : Mode exiting name.
        """
        if CliBase.__MODES:
            return CliBase.__MODES.pop()
        return None

    def load_commands_from_json(self, json_data):
        """Loads CLI commands from a JSON variable.

        The content of the JSON data should be a list of dictionaries, where
        every dictionary at least shoudl contain a field called 'command'
        which will contains the command to be executed.

        Args:
            json_data (json) : Variable with JSON data.

        Returns:
            None
        """
        lista = json.loads(json_data)
        for entry in lista:
            self.exec_user_input(entry['command'])

    def load_commands_from_file(self, filename):
        """Loads a file with the given filename with CLI commands in
        JSON format.

        Args:
            filename (string) : String with the filename that contains\
                    the json data.

        Returns:
            None
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.load_commands_from_json(json.dumps(data))
        except OSError:
            LOGGER.error('File not found {}'.format(filename), out=True)

    @staticmethod
    def command(label=None, desc=None):
        """Decorator that setup a function as a command.

        Args:
            label (str) : command label that identifies the command in the\
                command line (optional). If no value is entered, label is\
                taken from the @syntax decorator.

            desc (str) : command description (optional).

        Returns:
            func : Function wrapper.
        """

        def f_command(f):

            @wraps(f)
            def _wrapper(self, *args, **kwargs):
                return f(self, *args, **kwargs)

            LOGGER.debug(f, "YELLOW")
            module_name = sys._getframe(1).f_code.co_name
            CliBase._WALL.setdefault(module_name, [])
            if desc is not None:
                _desc = desc
            else:
                # if the wrapper is not a <method> or a <function> it is a
                # partial function, so the __doc__ is inside 'func' attribute.
                if inspect.ismethod(_wrapper) or inspect.isfunction(_wrapper):
                    _desc = _wrapper.__doc__
                else:
                    _desc = _wrapper.func.__doc__
            label_from_syntax = getattr(f, SYNTAX_ATTR, None)
            _label = f.__name__ if label_from_syntax is None else label_from_syntax.split()[0]
            CliBase._WALL[module_name].append((label if label else _label, _wrapper, _desc))
            return _wrapper

        return f_command
