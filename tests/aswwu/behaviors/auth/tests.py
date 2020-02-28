import tests.aswwu.behaviors.auth.subtests as subtests
import tests.conftest.testing_server as testing_server

def test_post_verify(testing_server):
    subtests.send_post_verify()