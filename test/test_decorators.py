import sys
import pytest

cliPath = '.'
sys.path.append(cliPath)

from base import CliBase
from decorators import params, arguments, defaults, argo, setargos, setdictos, syntax, setsyntax
from decorators import command, mode
from argtypes import Int, Str
from clierror import CliException


class CliTestModeClass(CliBase):

    def cmdloop(self):
        pass


class CliTestClass(CliBase):

    @params('field 1', 'field 2')
    def do_test_params(self, f1, f2):
        return f1, f2

    @arguments(Int, Str)
    def do_test_arguments(self, f1, f2):
        return f1, f2

    @defaults((Str, 'field'), (Int, 101))
    def do_test_defaults(self, f1, f2):
        return f1, f2

    @setargos
    @argo('f1', Int, 0)
    @argo('f2', Str, 'field 2')
    def do_test_argo_setargos(self, f1, f2):
        return f1, f2

    @setdictos
    @argo('f1', Str, 'field 1')
    @argo('f2', Int, 1)
    def do_test_argo_setdictos(self, f1, f2):
        return f1, f2

    @setsyntax
    @syntax('setsyntax f1 [f2]?')
    @argo('f1', Int, None)
    @argo('f2', Str, 'field 2')
    def do_test_syntax_zero_or_one(self, f1, f2):
        return f1, f2

    @setsyntax
    @syntax('setsyntax f1 [f2 | f3]?')
    @argo('f1', Int, None)
    @argo('f2', Str, 'field 2')
    @argo('f3', Int, 1)
    def do_test_setsyntax_zero_or_one_logic_or(self, f1, f2, f3):
        return f1, f2, f3

    @setsyntax
    @syntax('setsyntax f1 [f2]*')
    @argo('f1', Str, None)
    @argo('f2', Int, 0)
    def do_test_syntax_zero_or_more(self, f1, f2):
        return f1, f2

    @setsyntax
    @syntax('setsyntax f1 [f2 | f3]*')
    @argo('f1', Str, None)
    @argo('f2', Int, 0)
    @argo('f3', Str, 'field 3')
    def do_test_syntax_zero_or_more_logic_or(self, f1, f2, f3):
        return f1, f2, f3

    @setsyntax
    @syntax('setsyntax f1 [f2]+')
    @argo('f1', Str, None)
    @argo('f2', Int, 0)
    def do_test_syntax_one_or_more(self, f1, f2):
        return f1, f2

    @setsyntax
    @syntax('setsyntax f1 [f2 | f3]+')
    @argo('f1', Str, None)
    @argo('f2', Int, 0)
    @argo('f3', Int, 1)
    def do_test_syntax_one_or_more_logic_or(self, f1, f2, f3):
        return f1, f2, f3

    @setsyntax
    @syntax('setsyntax f1 [f2 | f3 [f4 | f5]?]?')
    @argo('f1', Int, None)
    @argo('f2', Str, 'field 2')
    @argo('f3', Str, 'key')
    @argo('f4', Str, 'id')
    @argo('f5', Str, 'name')
    def do_test_syntax_zero_or_one_with_inner_rule(self, f1, f2, f3, f4, f5):
        return f1, f2, f3, f4, f5

    @setsyntax
    @syntax('setsyntax f1 [f2]? [f3]+ [f4]* [f5]?')
    @argo('f1', Int, None)
    @argo('f2', Str, 'F2')
    @argo('f3', Str, 'F3')
    @argo('f4', Str, 'F4')
    @argo('f5', Str, 'F5')
    def do_test_syntax_multiple_arguments(self, f1, f2, f3, f4, f5):
        return f1, f2, f3, f4, f5


@command(CliBase)
def local_command(self, line):
    return 'local cmd command'


@mode(CliBase, CliTestModeClass)
def local_mode(self, line):
    return 'local cmd mode'


@command(CliBase)
@setsyntax
@syntax('local name [id]?')
@argo('name', Str, None)
@argo('id', Int, 0)
def local(self, name, id):
    return 'local cmd command: {}'.format(name), id


@mode(CliBase, CliTestModeClass)
@setsyntax
@syntax('lmode name [id]?')
@argo('name', Str, None)
@argo('id', Int, 0)
def localmode(self, name, id):
    return 'local cmd mode: {}'.format(name), id


def test_decorator_params():
    cli = CliTestClass()
    assert cli.do_test_params('') == ('field 1', 'field 2')
    assert cli.do_test_params('"custom f1"') == ('custom f1', 'field 2')
    assert cli.do_test_params('"custom f1" "custom f2"') == ('custom f1', 'custom f2')


def test_decorator_arguments():
    cli = CliTestClass()
    assert cli.do_test_arguments('100 "custom field"') == (100, 'custom field')
    with pytest.raises(CliException) as ex:
        cli.do_test_arguments('cien "custom field"')
    assert ex.value.message == "Wrong type of argument for command: test_arguments"


def test_decorator_defaults():
    cli = CliTestClass()
    assert cli.do_test_defaults('') == ('field', 101)
    assert cli.do_test_defaults('"custom field"') == ('custom field', 101)
    assert cli.do_test_defaults('"custom field" 202') == ('custom field', 202)


def test_decorator_argo_setargos():
    cli = CliTestClass()
    assert cli.do_test_argo_setargos('') == (0, 'field 2')
    assert cli.do_test_argo_setargos('50') == (50, 'field 2')
    assert cli.do_test_argo_setargos('101 "custom f2"') == (101, 'custom f2')


def test_decorator_argo_setdictos():
    cli = CliTestClass()
    assert cli.do_test_argo_setdictos('') == ('field 1', 1)
    assert cli.do_test_argo_setdictos('"custom f1"') == ('custom f1', 1)
    assert cli.do_test_argo_setdictos('"custom f1" 103') == ('custom f1', 103)
    assert cli.do_test_argo_setdictos('f1="custom f1"') == ('custom f1', 1)
    assert cli.do_test_argo_setdictos('f1="custom f1" f2=104') == ('custom f1', 104)
    assert cli.do_test_argo_setdictos('f2=105') == ('field 1', 105)
    assert cli.do_test_argo_setdictos('f2=106 f1="custom f1"') == ('custom f1', 106)


def test_decorator_setsyntax_zero_or_one():
    cli = CliTestClass()
    assert cli.do_test_syntax_zero_or_one('50') == (50, 'field 2')
    assert cli.do_test_syntax_zero_or_one('101 f2="custom f2"') == (101, 'custom f2')


def test_decorator_setsyntax_zero_or_one_logic_or():
    cli = CliTestClass()
    assert cli.do_test_setsyntax_zero_or_one_logic_or('50') == (50, 'field 2', 1)
    assert cli.do_test_setsyntax_zero_or_one_logic_or('101 f2="custom f2"') == (101, 'custom f2', 1)
    assert cli.do_test_setsyntax_zero_or_one_logic_or('101 f3=100') == (101, 'field 2', 100)
    with pytest.raises(CliException) as ex:
        cli.do_test_setsyntax_zero_or_one_logic_or('101 f2="garbage" f3=100')
    assert ex.value.message == '<f3=100> not found'


def test_decorator_setsyntax_zero_or_more():
    cli = CliTestClass()
    assert cli.do_test_syntax_zero_or_more('myshelf') == ('myshelf', 0)
    assert cli.do_test_syntax_zero_or_more('myshelf f2=100') == ('myshelf', 100)
    assert cli.do_test_syntax_zero_or_more('myshelf f2=100 f2=101') == ('myshelf', [100, 101])


def test_decorator_setsyntax_zero_or_more_logic_or():
    cli = CliTestClass()
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf') == ('myshelf', 0, 'field 3')
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf f2=100') == ('myshelf', 100, 'field 3')
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf f3="custom f3"') == ('myshelf', 0, 'custom f3')
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf \
            f2=100 f3="custom f3"') == ('myshelf', 100, 'custom f3')
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf \
            f2=100 f2=102') == ('myshelf', [100, 102], 'field 3')
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf \
            f3="f3-1" f3="f3-2"') == ('myshelf', 0, ['f3-1', 'f3-2'])
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf \
            f2=100 f3="custom f3" f2=200') == ('myshelf', [100, 200], 'custom f3')
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf \
            f2=100 f3="f3-1" f3="f3-2"') == ('myshelf', 100, ['f3-1', 'f3-2'])
    assert cli.do_test_syntax_zero_or_more_logic_or('myshelf \
            f2=200 f3="f3-1" f3="f3-2" f2=300') == ('myshelf', [200, 300], ['f3-1', 'f3-2'])


def test_decorator_setsyntax_one_or_more():
    cli = CliTestClass()
    with pytest.raises(CliException) as ex:
        cli.do_test_syntax_one_or_more('myshelf')
    assert ex.value.message == 'Number of Args: Too few arguments'
    assert cli.do_test_syntax_one_or_more('myshelf f2=100') == ('myshelf', 100)
    assert cli.do_test_syntax_one_or_more('myshelf f2=100 f2=101') == ('myshelf', [100, 101])


def test_decorator_setsyntax_one_or_more_logic_or():
    pass
    cli = CliTestClass()
    with pytest.raises(CliException) as ex:
        cli.do_test_syntax_one_or_more_logic_or('myshelf')
    assert ex.value.message == 'Number of Args: Too few arguments'
    assert cli.do_test_syntax_one_or_more_logic_or('myshelf f2=100') == ('myshelf', 100, 1)
    assert cli.do_test_syntax_one_or_more_logic_or('myshelf f2=100 f2=101') == ('myshelf', [100, 101], 1)
    assert cli.do_test_syntax_one_or_more_logic_or('myshelf f3=300') == ('myshelf', 0, 300)
    assert cli.do_test_syntax_one_or_more_logic_or('myshelf f3=300 f3=301') == ('myshelf', 0, [300, 301])
    assert cli.do_test_syntax_one_or_more_logic_or('myshelf f2=100 f3=300') == ('myshelf', 100, 300)
    assert cli.do_test_syntax_one_or_more_logic_or('myshelf \
            f2=100 f3=300 f2=101 f3=301') == ('myshelf', [100, 101], [300, 301])


def test_decorator_setsyntax_zero_or_one_with_inner_rule():
    cli = CliTestClass()
    assert cli.do_test_syntax_zero_or_one_with_inner_rule('50') == (50, 'field 2', 'key', 'id', 'name')
    assert cli.do_test_syntax_zero_or_one_with_inner_rule('50 f2="f2"') == (50, 'f2', 'key', 'id', 'name')
    assert cli.do_test_syntax_zero_or_one_with_inner_rule('50 f3="f3"') == (50, 'field 2', 'f3', 'id', 'name')
    assert cli.do_test_syntax_zero_or_one_with_inner_rule('50 \
            f3="f3" f4="f4"') == (50, 'field 2', 'f3', 'f4', 'name')


def test_decorator_setsyntax_multiple_arguments():
    cli = CliTestClass()
    assert cli.do_test_syntax_multiple_arguments('100 f3="+f3"') == (100, 'F2', '+f3', 'F4', 'F5')
    assert cli.do_test_syntax_multiple_arguments('100 \
            f3="+f3" f3="++f3"') == (100, 'F2', ['+f3', '++f3'], 'F4', 'F5')
    assert cli.do_test_syntax_multiple_arguments('100 \
            f2="?f2" f3="+f3"') == (100, '?f2', '+f3', 'F4', 'F5')
    assert cli.do_test_syntax_multiple_arguments('100 \
            f3="+f3" f5="?f5"') == (100, 'F2', '+f3', 'F4', '?f5')
    assert cli.do_test_syntax_multiple_arguments('100 \
            f3="+f3" f4="*f4"') == (100, 'F2', '+f3', '*f4', 'F5')
    assert cli.do_test_syntax_multiple_arguments('100 \
            f2="?f2" f3="+f3" f4="*f4" f5="?f5"') == (100, '?f2', '+f3', '*f4', '?f5')
    assert cli.do_test_syntax_multiple_arguments('100 \
            f2="?f2" f3="+f3" f3="++f3" f4="*f4" f4="**f4" f5="?f5"') == (100, '?f2', ['+f3', '++f3'], ['*f4', '**f4'], '?f5')
    with pytest.raises(CliException) as ex:
        cli.do_test_syntax_multiple_arguments('100 f2="?f2" f4="*f4" f5="?f5"')
    assert ex.value.message == '<f4=*f4> not found'
    with pytest.raises(CliException) as ex:
        cli.do_test_syntax_multiple_arguments('100 f3="+f3" f2="?f2" f4="*f4" f5="?f5"')
    assert ex.value.message == '<f2=?f2> not found'


def test_decorator_command():
    cli = CliTestClass()
    assert cli.do_local_command('') == 'local cmd command'


def test_decorator_command_with_syntax():
    cli = CliTestClass()
    assert cli.do_local('"shelf"') == ('local cmd command: shelf', 0)


def test_decorator_mode():
    cli = CliTestClass()
    assert cli.do_local_mode('') == 'local cmd mode'


def test_decorator_mode_with_syntax():
    cli = CliTestClass()
    assert cli.do_localmode('"shelf"') == ('local cmd mode: shelf', 0)
