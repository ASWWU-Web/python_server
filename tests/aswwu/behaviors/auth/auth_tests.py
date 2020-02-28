from tests.aswwu.behaviors.auth.subtests import send_post_verify
from tests.conftest import testing_server


def test_post_verify(testing_server):
    send_post_verify()
