from tests.aswwu.behaviors.elections.elections_subtests import *
from tests.conftest import testing_server


def test_post_election(testing_server):
    send_post_election()


def test_get_election(testing_server):
    send_get_election()


def test_get_current(testing_server):
    send_get_current()


def test_post_position(testing_server):
    send_post_position()


def test_get_position(testing_server):
    send_get_position()
