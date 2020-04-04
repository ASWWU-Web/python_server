import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.utils as utils
from tests.aswwu.data.paths import USERS_PATH
import json

DEFAULT_STATUS = 'Student'
DEFAULT_ROLES = ['None', '']


def assert_verify_response(response, user):
    response_text = json.loads(response.text)
    assert(response.status_code == 200)
    assert (response_text['token'].split('|')[0] == user['wwuid'])
    assert (response_text['user']['username'] == user['username'])
    assert (response_text['user']['wwuid'] == user['wwuid'])
    assert (response_text['user']['roles'] in DEFAULT_ROLES)
    assert (response_text['user']['status'] == DEFAULT_STATUS)
    assert (response_text['user']['full_name'] == user['full_name'])
