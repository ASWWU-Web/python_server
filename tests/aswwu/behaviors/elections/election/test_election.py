from tests.aswwu.behaviors.elections.election.election_subtests import *
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.aswwu.behaviors.auth.auth_subtests as auth_subtests
from tests.conftest import testing_server


def test_post_election(testing_server):
    send_post_election()


def test_get_election(testing_server):
    election_data = send_post_election()
    send_get_election(election_data)


def test_get_current(testing_server):
    election_data = send_post_dynamic_election()
    send_get_current(election_data)


def test_get_specified_election(testing_server):
    election_data = send_post_election()
    send_get_specified_election(election_data)
