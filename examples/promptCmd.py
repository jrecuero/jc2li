from __future__ import unicode_literals
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
# import click
from fuzzyfinder import fuzzyfinder
from pygments.lexers.sql import SqlLexer
import sys


class CliCompleter(Completer):

    CliKeywords = ['exit', 'run', 'execute']

    def get_completions(self, document, completeEvent):
        wordBeforeCursor = document.get_word_before_cursor(WORD=True)
        matches = fuzzyfinder(wordBeforeCursor, CliCompleter.CliKeywords)
        for m in matches:
            yield Completion(m, start_position=-len(wordBeforeCursor))


class CliValidator(Validator):

    def validate(self, document):
        lineSplit = document.text.split() if document.text else None
        found = document.find_all('none') if lineSplit and 'none' in lineSplit else None
        if found:
            raise ValidationError(found[0], 'none in document')
        return True


class Cli(object):

    test_style = style_from_dict({Token.Toolbar: '#ffffff italic bg:#007777', })

    def __init__(self):
        self._lastCmd = None
        self._cmdDict = {'exit': self.do_exit}

    @property
    def LastCmd(self):
        return self._lastCmd

    @LastCmd.setter
    def LastCmd(self, theCmd):
        self._lastCmd = theCmd

    def getBottomToolbarTokens(self, cli):
        # cmd = cli.current_buffer.history.strings[-1]
        # cmd = '' if cmd == 'exit' else cmd
        return [(Token.Toolbar, 'Command: {} '.format(self.LastCmd)), ]

    def do_exit(self, line):
        print('Last command: {}'.format(self.LastCmd))
        sys.exit(0)

    def isCommand(self, theCmd):
        return theCmd in self._cmdDict.keys()

    def execCommand(self, theCmd, theUserInput):
        self._cmdDict[theCmd](theUserInput)


if __name__ == '__main__':
    cli = Cli()
    while True:
        userInput = prompt('SQL> ',
                           history=FileHistory('history.txt'),
                           auto_suggest=AutoSuggestFromHistory(),
                           completer=CliCompleter(),
                           lexer=SqlLexer,
                           get_bottom_toolbar_tokens=cli.getBottomToolbarTokens,
                           style=Cli.test_style,
                           validator=CliValidator(),
                           refresh_interval=1)
        # click.echo_via_pager(userInput)
        print(userInput)
        # message = click.edit()
        if userInput:
            cmd = userInput.split()[0]
            if cli.isCommand(cmd):
                cli.execCommand(cmd, userInput)
            cli.LastCmd = userInput
