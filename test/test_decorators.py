import sys
import pytest

cliPath = '.'
sys.path.append(cliPath)

from base import Cli
from decorators import argo, syntax, setsyntax
from argtypes import Int, Str
from clierror import CliException


class CliTestModeClass(Cli):

    def cmdloop(self):
        pass


class CliTestWorkClass(Cli):

    @Cli.command('ss')
    @setsyntax
    @syntax('setsyntax f1 <F2>')
    @argo('f1', Str, None)
    @argo('F2', Str, 'F2')
    def do_test_syntax_constant(self, f1, f2):
        return f1, f2


class CliTestClass(Cli):

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
    @syntax('setsyntax f1 [f2 | f3]!')
    @argo('f1', Str, None)
    @argo('f2', Int, 0)
    @argo('f3', Int, 1)
    def do_test_syntax_one_only_option(self, f1, f2, f3):
        return f1, f2, f3

    @setsyntax
    @syntax('setsyntax f1 <F2>')
    @argo('f1', Str, None)
    @argo('F2', Str, None)
    def do_test_syntax_constant(self, f1, f2):
        return f1, f2

    @setsyntax
    @syntax('setsyntax f1 [<F2> | <F3>]!')
    @argo('f1', Str, None)
    @argo('F2', Str, 'F2')
    @argo('F3', Str, 'F3')
    def do_test_syntax_constant_option(self, f1, f2, f3):
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


def test_decorator_setsyntax_work():
    CliTestWorkClass()


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


def test_decorator_setsyntax_one_only_option():
    pass
    cli = CliTestClass()
    with pytest.raises(CliException) as ex:
        cli.do_test_syntax_one_only_option('myshelf')
    assert ex.value.message == 'Number of Args: Too few arguments'
    assert cli.do_test_syntax_one_only_option('myshelf f2=100') == ('myshelf', 100, 1)
    assert cli.do_test_syntax_one_only_option('myshelf f3=300') == ('myshelf', 0, 300)
    with pytest.raises(CliException) as ex:
        assert cli.do_test_syntax_one_only_option('myshelf f2=100 f3=300') == ('myshelf', 100, 300)
    assert ex.value.message == '<f3=300> not found'


def test_decorator_setsyntax_constant():
    pass
    cli = CliTestClass()
    with pytest.raises(CliException) as ex:
        cli.do_test_syntax_constant('myshelf')
    assert ex.value.message == 'Mandatory argument is not present'
    assert cli.do_test_syntax_constant('myshelf F2') == ('myshelf', 'F2')


def test_decorator_setsyntax_constant_option():
    pass
    cli = CliTestClass()
    with pytest.raises(CliException) as ex:
        cli.do_test_syntax_constant_option('myshelf')
    assert ex.value.message == 'Number of Args: Too few arguments'
    assert cli.do_test_syntax_constant_option('myshelf F2') == ('myshelf', 'F2', 'F3')
    assert cli.do_test_syntax_constant_option('myshelf F3') == ('myshelf', 'F2', 'F3')


@pytest.mark.parametrize("theInput, theExpected",
                         (('50', (50, 'field 2', 'key', 'id', 'name')),
                          ('50 f2="f2"', (50, 'f2', 'key', 'id', 'name')),
                          ('50 f3="f3"', (50, 'field 2', 'f3', 'id', 'name')),
                          ('50 f3="f3" f4="f4"', (50, 'field 2', 'f3', 'f4', 'name'))))
def test_decorator_setsyntax_zero_or_one_with_inner_rule(theInput, theExpected):
    cli = CliTestClass()
    assert cli.do_test_syntax_zero_or_one_with_inner_rule(theInput) == theExpected
    # assert cli.do_test_syntax_zero_or_one_with_inner_rule('50') == (50, 'field 2', 'key', 'id', 'name')
    # assert cli.do_test_syntax_zero_or_one_with_inner_rule('50 f2="f2"') == (50, 'f2', 'key', 'id', 'name')
    # assert cli.do_test_syntax_zero_or_one_with_inner_rule('50 f3="f3"') == (50, 'field 2', 'f3', 'id', 'name')
    # assert cli.do_test_syntax_zero_or_one_with_inner_rule('50 \
    #         f3="f3" f4="f4"') == (50, 'field 2', 'f3', 'f4', 'name')


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
