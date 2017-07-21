import sys

cliPath = '.'
sys.path.append(cliPath)

from journal import Journal


def test_journal():
    journal = Journal()
    assert len(journal.path) == 0
    assert len(journal.argos.keys()) == 0
    assert journal.traverseNode is None
