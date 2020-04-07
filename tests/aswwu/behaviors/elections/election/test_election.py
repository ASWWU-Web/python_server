from tests.aswwu.behaviors.elections.election.election_subtests import *
from tests.conftest import testing_server


def test_post_election(testing_server):
    send_post_election()


def test_get_election(testing_server):
    send_get_election()


def test_get_current(testing_server):
    send_post_dynamic_election()
    send_get_current()
