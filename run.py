__docformat__ = 'restructuredtext en'

#------------------------------------------------------------------------------
#  _                            _
# (_)_ __ ___  _ __   ___  _ __| |_ ___
# | | '_ ` _ \| '_ \ / _ \| '__| __/ __|
# | | | | | | | |_) | (_) | |  | |_\__ \
# |_|_| |_| |_| .__/ \___/|_|   \__|___/
#             |_|
#------------------------------------------------------------------------------
#
import sys
import loggerator
import argparse
import importlib
import json


#------------------------------------------------------------------------------
#
#   ___ ___  _ __  ___| |_ __ _ _ __ | |_ ___
#  / __/ _ \| '_ \/ __| __/ _` | '_ \| __/ __|
# | (_| (_) | | | \__ \ || (_| | | | | |_\__ \
#  \___\___/|_| |_|___/\__\__,_|_| |_|\__|___/
#
#------------------------------------------------------------------------------
#
MODULE = 'CLI.run'
LOGGER = loggerator.getLoggerator(MODULE)


#------------------------------------------------------------------------------
#            _                     _   _
#  ___ _   _| |__  _ __ ___  _   _| |_(_)_ __   ___  ___
# / __| | | | '_ \| '__/ _ \| | | | __| | '_ \ / _ \/ __|
# \__ \ |_| | |_) | | | (_) | |_| | |_| | | | |  __/\__ \
# |___/\__,_|_.__/|_|  \___/ \__,_|\__|_|_| |_|\___||___/
#
#------------------------------------------------------------------------------
#
def load_module(module, skip_exception=False):
    """Loads the given module.

    Args:
        module (string) : Module to load.
        skip_exception (bool) : True is exception should be skipped.

    Returns:
        module : Python module loaded.
    """
    if skip_exception:
        mod = importlib.import_module(module)
    else:
        try:
            mod = importlib.import_module(module)
        except:
            LOGGER.error('Module {0} not found'.format(module), out=True)
            sys.exit(0)
    return mod


def create_cli(module):
    """Create a cli using the given module.

    The module will cotains all CLI commands to be used.

    Args:
        module (module) : Python module with CLI commands.

    Returns:
        :class:`Cli` : Cli object.
    """
    try:
        cli = getattr(module, module.EXPORT)()
    except AttributeError:
        LOGGER.error("Module {0} don't have EXPORT attribute".format(module), out=True)
        sys.exit(0)
    return cli


def setup_kwargs(cli):
    """Setups kwargs to be passed to the CLI running method.

    Args:
        cli (:class:`Cli`) : Cli instance.

    Returns:
        :any:`dict` : Dictionary with kwargs to be passed to CLI.
    """
    try:
        cli_kwargs = {'prompt': 'CLI> '}
        cli_kwargs.update(getattr(mod, mod.EXPORT_KWARGS))
    except AttributeError:
        pass
    return cli_kwargs


def execute_command(cli, command):
    """Executes the given CLI command.

    Args:
        command (str) : String with the CLI command.

    Returns:
        None
    """
    LOGGER.display('execute {}'.format(command))
    cli.exec_user_input(command)


def execute_file(cli, filename, raw=False):
    """Executes all commands in the given file.

    Args:
        filename (str) : Filename with all CLI commands.

        raw (bool) : True if file contains commands in text format, False if\
                commands are in JSON format.
    """
    LOGGER.display('execute commands in file {}'.format(filename))
    if raw:
        commands = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    commands.append({'command': line.rstrip()})
            cli.load_commands_from_json(json.dumps(commands))
        except OSError:
            LOGGER.display('File not found {}'.format(filename))
    else:
        cli.load_commands_from_file(filename)


def test(cli, module, filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        log_module = getattr(module, 'MODULE')
        cli_logger = loggerator.getLoggerator(log_module)
        cli_logger.redirect_out_to()
        for entry in data:
            cli.exec_user_input(entry['command'])
        cli_logger.stop_redirect_out()
        LOGGER.display('redirected output is: ')
        output = cli_logger.get_redirect_buffer()
        LOGGER.display(cli_logger.get_redirect_buffer())
        LOGGER.display(output.rstrip().split('\n'))
        LOGGER.display(cli_logger.get_redirect_buffer(True))
    except OSError:
        LOGGER.error('File not found {}'.format(filename), out=True)


#------------------------------------------------------------------------------
#                  _
#  _ __ ___   __ _(_)_ __
# | '_ ` _ \ / _` | | '_ \
# | | | | | | (_| | | | | |
# |_| |_| |_|\__,_|_|_| |_|
#
#------------------------------------------------------------------------------
#
if __name__ == '__main__':
    LOGGER.info("CLI APPLICATION", extended=(('FG', 'BLUE'), ('BG', 'YELLOW'), ))
    LOGGER.info("---------------", "RED")

    parser = argparse.ArgumentParser(description="CLI application launcher.")
    parser.add_argument('--mod', '-M', action='store', help='Module with CLI commands', metavar='MODULE')
    parser.add_argument('--echo', action='store_true', help='Echo mode')
    parser.add_argument('--exception', '-X', action='store_true', help='Exception mode')
    parser.add_argument('--exec', '-E', action='store', help='Execute command', metavar='CMD')
    parser.add_argument('--file', '-f', action='store', help='Execute command inside file', metavar='FILE')
    parser.add_argument('--raw', '-r', action='store_true', help='File in raw format')
    parser.add_argument('--test', '-t', action='store', help='Test file with commands and results', metavar='FILE')
    args = parser.parse_args()

    if args.mod is None:
        sys.exit(0)

    mod = load_module(args.mod, args.exception)
    cli = create_cli(mod)

    if args.exec:
        execute_command(cli, args.exec)
        sys.exit(0)

    if args.test:
        test(cli, mod, args.test)
        sys.exit(0)

    if args.file:
        execute_file(cli, args.file, args.raw)
        sys.exit(0)

    cli_kwargs = setup_kwargs(cli)
    cli.run(**cli_kwargs)
