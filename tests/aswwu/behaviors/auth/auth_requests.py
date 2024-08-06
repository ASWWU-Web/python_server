import os
import requests
import settings

BASE_URL = settings.environment['base_url'] + ':' + str(settings.environment['port'])
VERIFY_URL = '/'.join([BASE_URL, 'verify'])
ROLES_URL = '/'.join([BASE_URL, 'roles'])


def post_verify(wwuid, full_name, email, session=None):
    session = requests.Session() if session is None else session

    post_data = {
        'secret_key': os.environ.get("SAML_ENDPOINT_KEY"),
        'employee_id': wwuid,
        'full_name': full_name,
        'email_address': email,
    }
    resp = session.post(VERIFY_URL, post_data)
    return resp


def get_verify(session=None):
    session = requests.Session() if session is None else session

    resp = session.get(VERIFY_URL)
    return resp

def get_logout(session=None):
    session = requests.Session() if session is None else session

    resp = session.get('/'.join([BASE_URL, 'logout']))
    return resp


def post_roles(wwuid, roles):
    """
    sets the roles of the user with the provided wwuid to only those
    listed in the provided roles array
    :param wwuid: the wwuid of the user whos roles need to be updated
    :param roles: an array of strings, where each string is a single role
    :return:
    """
    roles_endpoint = '/'.join([ROLES_URL, wwuid])
    post_data = {'roles': roles}
    resp = requests.post(roles_endpoint, json=post_data)
    return resp
