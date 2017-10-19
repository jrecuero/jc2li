# import sys
#
# cliPath = '.'
# sys.path.append(cliPath)

from jc2li.journal import Journal


def test_journal():
    journal = Journal()
    assert len(journal.path) == 0
    assert len(journal.argos.keys()) == 0
    assert journal.traverse_node is None
