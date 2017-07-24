import sys

cliPath = '.'
sys.path.append(cliPath)

from journal import Journal


def test_journal():
    journal = Journal()
    assert len(journal.Path) == 0
    assert len(journal.Argos.keys()) == 0
    assert journal.TraverseNode is None
