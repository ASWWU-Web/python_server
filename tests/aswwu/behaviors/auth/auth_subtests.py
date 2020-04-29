import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.utils as utils
from tests.aswwu.data.paths import USERS_PATH
import json
from requests import Session, cookies

DEFAULT_STATUS = 'Student'
DEFAULT_ROLES = ['None', '']


def assert_verify_login(user):
    """
    Use this function to make sure a test user is logged in on the server.
    Tests whether a user that authenticated with SAML can use the verify endpoint.
    :param user: a user object loaded from a csv file
    :return: (text, user) the text of the get verify response as an associative array
    and the authenticated session for subsequent requests
    """
    post_response = auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
    assert_verify_response(post_response, user)
    auth_token = json.loads(post_response.text)['token']
    auth_cookie = cookies.create_cookie('token', auth_token)
    session = Session()
    session.cookies.set_cookie(auth_cookie)
    get_response = auth_requests.get_verify(session)
    assert_verify_response(get_response, user)
    return json.loads(get_response.text), session


def assert_verify_response(response, user):
    """
    Tests whether data returned from the verify endpoint matches the provided user.
    :param response: the response from the verify endpoint
    :param user: a user object loaded form a csv file
    :return: None
    """
    response_text = json.loads(response.text)
    assert(response.status_code == 200)
    assert (response_text['user']['username'] == user['username'])
    assert (response_text['user']['wwuid'] == user['wwuid'])
    assert (response_text['user']['roles'] in DEFAULT_ROLES)
    assert (response_text['user']['status'] == DEFAULT_STATUS)
    assert (response_text['user']['full_name'] == user['full_name'])
    assert (response_text['token'].split('|')[0] == user['wwuid'])
