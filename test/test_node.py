import sys
# import pytest

cliPath = '.'
sys.path.append(cliPath)

from node import Node, Hook, Start, End
from common import Argument, Arguments
from argtypes import Int, Str


def test_node():
    node = Node(None)
    assert node.Parent is None
    assert node.Argo is None
    assert len(node.Children) == 0


def test_hook():
    node = Hook(None)
    assert node.Parent is None
    assert node.Parents == []
    assert node.Argo is None
    assert len(node.Children) == 0
    assert node.Name is None
    assert node.Type is None
    assert node.Label == 'Hook'
    assert node.Default is None
    node.Parent = None
    assert node.Parents == [None]
    node.Parent = None
    assert node.Parents == [None, None]
    assert node.Ancestor is None


def test_build_nodes():
    root = Start()
    argos = [Argument('tname', str, 'myname'),
             Argument('tid', str, 'myid'),
             Argument('tsig', str, 'mysig')]
    travWrite = root
    for arg in argos:
        child = Node(arg)
        travWrite.addChild(child)
        travWrite = child
    travWrite.addChild(End())

    travRead = root
    while travRead.Children == 0:
        children = travRead.Children
        assert len(children) == 1, 'node: {}'.format(travRead.Name)
        travRead = children[0]

    travRead = root
    assert travRead.Label == 'Start'
    travRead = travRead.Children[0]
    assert travRead.Name == 'tname'
    assert travRead.Label == 'tname'
    travRead = travRead.Children[0]
    assert travRead.Name == 'tid'
    assert travRead.Label == 'tid'
    travRead = travRead.Children[0]
    assert travRead.Name == 'tsig'
    assert travRead.Label == 'tsig'
    travRead = travRead.Children[0]
    assert travRead.Name is None
    assert travRead.Label == 'End'


def test_build_tree_prototype():
    node1 = Node(Argument('tname', str, 'myname'))
    hookEnter = Hook()
    node21 = Node(Argument('tid', str, 'myid'))
    node22 = Node(Argument('tsig', str, 'mysig'))
    end = End()

    root = Start()
    root.addChild(node1)
    node1.addChild(hookEnter)
    hookEnter.addChild(end)
    hookEnter.addChild(node21)
    hookEnter.addChild(node22)
    node21.addChild(end)
    node22.addChild(end)

    path = ['tname', 'tid']
    nodePath = root.findPath(path)
    assert [x.Name for x in nodePath] == path

    path = ['tname', 'tsig']
    nodePath = root.findPath(path)
    assert [x.Name for x in nodePath] == path

    path = ['tid', 'tid']
    nodePath = root.findPath(path)
    assert nodePath is None

    path = ['tname', 'talias']
    nodePath = root.findPath(path)
    assert nodePath is None

    path = ['tname', ]
    nodePath = root.findPath(path)
    assert len(nodePath) == 1
    assert [x.Name for x in nodePath] == path
    assert nodePath[0].Name == 'tname'
    path = ['tsig', ]
    nodePath = nodePath[0].findPath(path)
    assert len(nodePath) == 1
    assert [x.Name for x in nodePath] == path
    assert nodePath[0].Name == 'tsig'


def test_build_tree_from_rules():
    argos = Arguments()
    argos.addArgument(Argument('t1', Str, None))
    argos.addArgument(Argument('t2', Int, 0))
    argos.addArgument(Argument('t3', Str, 'myself'))
    argos.index()
    rules = [{'counter': 0, 'type': '1', 'args': 't1'},
             {'counter': 1, 'type': '?', 'args': [{'counter': 0, 'type': '1', 'args': 't2'},
                                                  {'counter': 0, 'type': '1', 'args': 't3'}]},
             {'counter': 2, 'type': '0', 'args': None}, ]
    trav = Start()
    for rule in rules:
        newtrav = trav.buildChildrenNodeFromRule(rule, argos)
        trav = newtrav


if __name__ == '__main__':
    pass
