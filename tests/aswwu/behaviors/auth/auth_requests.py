import requests
from settings import keys, testing


VERIFY_URL = testing['base_url'] + ':' + testing['port'] + '/' + 'verify'


def post_verify(wwuid, full_name, email):
    post_data = {
        'secret_key': keys["samlEndpointKey"],
        'employee_id': wwuid,
        'full_name': full_name,
        'email_address': email,
    }
    resp = requests.post(VERIFY_URL, post_data)
    return resp


def get_verify():
    resp = requests.get(VERIFY_URL)
    assert (resp.status_code == 200)
    return resp
