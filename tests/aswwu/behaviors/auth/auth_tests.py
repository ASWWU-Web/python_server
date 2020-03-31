from tests.aswwu.behaviors.auth.auth_subtests import send_post_verify, send_get_verify
from tests.conftest import testing_server


def test_post_verify(testing_server):
    send_post_verify()


def test_get_verify(testing_server):
    send_get_verify()
