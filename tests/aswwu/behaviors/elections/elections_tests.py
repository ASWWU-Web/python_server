from tests.aswwu.behaviors.elections.elections_subtests import send_post_election, send_get_election
from tests.conftest import testing_server


def test_post_election(testing_server):
    send_post_election()


def test_get_election(testing_server):
    send_get_election()
