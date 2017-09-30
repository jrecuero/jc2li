import sys
import pytest

cliPath = '.'
sys.path.append(cliPath)

from node import Node, Hook, Start, End
from arguments import Argument, Arguments
from argtypes import Int, Str
from clierror import CliException


def test_node():
    node = Node(None)
    assert node.parent is None
    assert node.argo is None
    assert len(node.children) == 0


def test_hook():
    node = Hook()
    assert node.parent is None
    assert node.parents == []
    assert node.argo is None
    assert len(node.children) == 0
    assert node.name is None
    assert node.argtype is None
    assert node.label == 'Hook'
    assert node.default is None
    node.parent = None
    assert node.parents == [None]
    node.parent = None
    assert node.parents == [None, None]
    assert node.ancestor is None


def test_build_nodes():
    root = Start()
    argos = [Argument('tname', Str, default='myname'),
             Argument('tid', Str, default='myid'),
             Argument('tsig', Str, default='mysig')]
    trav_write = root
    for arg in argos:
        child = Node(arg)
        trav_write.add_child(child)
        trav_write = child
    trav_write.add_child(End())

    trav_read = root
    while trav_read.children == 0:
        children = trav_read.children
        assert len(children) == 1, 'node: {}'.format(trav_read.name)
        trav_read = children[0]

    trav_read = root
    assert trav_read.label == 'Start'
    trav_read = trav_read.children[0]
    assert trav_read.name == 'tname'
    assert trav_read.label == 'tname'
    trav_read = trav_read.children[0]
    assert trav_read.name == 'tid'
    assert trav_read.label == 'tid'
    trav_read = trav_read.children[0]
    assert trav_read.name == 'tsig'
    assert trav_read.label == 'tsig'
    trav_read = trav_read.children[0]
    assert trav_read.name is None
    assert trav_read.label == 'End'


def test_build_tree_prototype():
    node1 = Node(Argument('tname', Str, default='myname'))
    hook_enter = Hook()
    node21 = Node(Argument('tid', Str, default='myid'))
    node22 = Node(Argument('tsig', Str, default='mysig'))
    end = End()

    root = Start()
    root.add_child(node1)
    node1.add_child(hook_enter)
    hook_enter.add_child(end)
    hook_enter.add_child(node21)
    hook_enter.add_child(node22)
    node21.add_child(end)
    node22.add_child(end)

    path = ['tname', 'tid']
    node_path = root.find_path(path)
    assert [x.name for x in node_path] == path

    path = ['tname', 'tsig']
    node_path = root.find_path(path)
    assert [x.name for x in node_path] == path

    path = ['tid', 'tid']
    with pytest.raises(CliException) as ex:
        node_path = root.find_path(path)
    assert ex.value.message == '<tid> not found'

    path = ['tname', 'talias']
    with pytest.raises(CliException) as ex:
        node_path = root.find_path(path)
    assert ex.value.message == '<talias> not found'

    path = ['tname', ]
    node_path = root.find_path(path)
    assert len(node_path) == 1
    assert [x.name for x in node_path] == path
    assert node_path[0].name == 'tname'
    path = ['tsig', ]
    node_path = node_path[0].find_path(path)
    assert len(node_path) == 1
    assert [x.name for x in node_path] == path
    assert node_path[0].name == 'tsig'


def test_build_tree_from_rules():
    argos = Arguments()
    argos.add_argument(Argument('t1', Str))
    argos.add_argument(Argument('t2', Int, default=0))
    argos.add_argument(Argument('t3', Str, default='myself'))
    argos.index()
    rules = [{'counter': 0, 'type': '1', 'args': 't1'},
             {'counter': 1, 'type': '?', 'args': [{'counter': 0, 'type': '1', 'args': 't2'},
                                                  {'counter': 0, 'type': '1', 'args': 't3'}]},
             {'counter': 2, 'type': '0', 'args': None}, ]
    trav = Start()
    for rule in rules:
        new_trav = trav.build_children_node_from_rule(rule, argos)
        trav = new_trav
