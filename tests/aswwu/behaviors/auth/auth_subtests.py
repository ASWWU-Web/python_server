import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.utils as utils
from tests.aswwu.data.paths import USERS_PATH
import json
from settings import keys, testing


def send_get_verify():
    resp = auth_requests.get_verify()
    assert(resp.status_code == 200)


def send_post_verify():
    DEFAULT_STATUS = 'Student'
    DEFAULT_ROLES = 'None'
    users = utils.load_csv(USERS_PATH)
    for user in users:
        resp = auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
        resp_text = json.loads(resp.text)
        assert (resp.status_code == 200)
        assert (resp_text['token'].split('|')[0] == user['wwuid'])
        assert (resp_text['user']['username'] == user['username'])
        assert (resp_text['user']['wwuid'] == user['wwuid'])
        assert (resp_text['user']['roles'] == DEFAULT_ROLES)
        assert (resp_text['user']['status'] == DEFAULT_STATUS)
        assert (resp_text['user']['full_name'] == user['full_name'])