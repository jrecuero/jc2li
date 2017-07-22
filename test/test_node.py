import sys
import pytest

cliPath = '.'
sys.path.append(cliPath)

from node import Node, Hook, Start, End
from argument import Argo


def test_node():
    node = Node(None)
    assert node.parent is None
    assert node.argo is None
    assert len(node.children) == 0


def test_hook():
    node = Hook(None)
    assert node.parent is None
    assert node.parents == []
    assert node.argo is None
    assert len(node.children) == 0
    assert node.name is None
    assert node.type is None
    assert node.label == 'Hook'
    assert node.default is None
    node.parent = None
    assert node.parents == [None]
    node.parent = None
    assert node.parents == [None, None]
    assert node.ancestor is None


def test_build_nodes():
    root = Start()
    argos = [{'name': 'tname', 'type': str, 'default': 'myname'},
             {'name': 'tid', 'type': str, 'default': 'myid'},
             {'name': 'tsig', 'type': str, 'default': 'mysig'}, ]
    travWrite = root
    for x in argos:
        child = Node(Argo(x))
        travWrite.addChild(child)
        travWrite = child
    travWrite.addChild(End())

    travRead = root
    while travRead.children == 0:
        children = travRead.children
        assert len(children) == 1, 'node: {}'.format(travRead.name)
        travRead = children[0]

    travRead = root
    assert travRead.label == 'Start'
    travRead = travRead.children[0]
    assert travRead.name == 'tname'
    assert travRead.label == 'tname'
    travRead = travRead.children[0]
    assert travRead.name == 'tid'
    assert travRead.label == 'tid'
    travRead = travRead.children[0]
    assert travRead.name == 'tsig'
    assert travRead.label == 'tsig'
    travRead = travRead.children[0]
    assert travRead.name is None
    assert travRead.label == 'End'


def test_build_tree_prototype():
    node1 = Node(Argo({'name': 'tname', 'type': str, 'default': 'myname'}))
    hookEnter = Hook()
    node21 = Node(Argo({'name': 'tid', 'type': str, 'default': 'myid'}))
    node22 = Node(Argo({'name': 'tsig', 'type': str, 'default': 'mysig'}))
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
    assert [x.name for x in nodePath] == path

    path = ['tname', 'tsig']
    nodePath = root.findPath(path)
    assert [x.name for x in nodePath] == path

    path = ['tid', 'tid']
    with pytest.raises(NameError) as err:
        nodePath = root.findPath(path)
    assert err.value.message == '<tid> not found'

    path = ['tname', 'talias']
    with pytest.raises(NameError) as err:
        nodePath = root.findPath(path)
    assert err.value.message == '<talias> not found'

    path = ['tname', ]
    nodePath = root.findPath(path)
    assert len(nodePath) == 1
    assert [x.name for x in nodePath] == path
    assert nodePath[0].name == 'tname'
    path = ['tsig', ]
    nodePath = nodePath[0].findPath(path)
    assert len(nodePath) == 1
    assert [x.name for x in nodePath] == path
    assert nodePath[0].name == 'tsig'


def test_build_tree_from_rules():
    rules = [{'counter': 0, 'type': '1', 'args': 't1'},
             {'counter': 1, 'type': '?', 'args': [{'counter': 0, 'type': '1', 'args': 't2'},
                                                  {'counter': 0, 'type': '1', 'args': 't3'}]},
             {'counter': 2, 'type': '0', 'args': None}, ]
    trav = Start()
    for rule in rules:
        newtrav = trav.buildChildrenNodeFromRule(rule)
        trav = newtrav


if __name__ == '__main__':
    pass
