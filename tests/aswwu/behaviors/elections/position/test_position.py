from tests.aswwu.behaviors.elections.position.position_subtests import *
from tests.conftest import testing_server


def test_post_position(testing_server):
    send_post_position()


def test_get_position(testing_server):
    send_get_position()
