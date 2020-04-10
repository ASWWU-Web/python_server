import requests
from settings import keys, testing

BASE_URL = testing['base_url'] + ':' + str(testing['port'])
VERIFY_URL = '/'.join([BASE_URL, 'verify'])
ROLES_URL = '/'.join([BASE_URL, 'roles'])


def post_verify(wwuid, full_name, email, session=requests.Session()):
    post_data = {
        'secret_key': keys["samlEndpointKey"],
        'employee_id': wwuid,
        'full_name': full_name,
        'email_address': email,
    }
    resp = session.post(VERIFY_URL, post_data)
    return resp


def get_verify(session=requests.Session()):
    resp = session.get(VERIFY_URL)
    return resp


def post_roles(wwuid, roles):
    roles_endpoint = '/'.join([ROLES_URL, wwuid])
    post_data = {'roles': roles}
    resp = requests.post(roles_endpoint, json=post_data)
    return resp
