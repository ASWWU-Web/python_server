import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import requests
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_response, assert_verify_login
from tests.conftest import testing_server
from tests.utils import load_csv
from tests.aswwu.data.paths import USERS_PATH
import json


def test_post_verify(testing_server):
    users = load_csv(USERS_PATH)
    for user in users:
        response = auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
        assert_verify_response(response, user)


def test_get_verify(testing_server):
    users = load_csv(USERS_PATH)
    for user in users:
        assert_verify_login(user)


def test_post_roles(testing_server):
    users = load_csv(USERS_PATH)
    for user in users:
        assert_verify_login(user)
        roles = ['demo_role_1', 'demo_role_2']
        response = auth_requests.post_roles(user['wwuid'], roles)
        assert (response.status_code == 201)
        response_roles_data = json.loads(response.text)['user']['roles']
        expected_roles_data = ','.join(roles)
        assert (response_roles_data == expected_roles_data)

