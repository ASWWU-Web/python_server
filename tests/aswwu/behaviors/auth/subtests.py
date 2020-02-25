import requests
from settings import keys, testing


def post_verify(wwuid, full_name, email):
    url = testing['base_url'] + testing['port'] + 'verify'
    post_data = {
        'secret_key': keys["samlEndpointKey"],
        'employee_id': wwuid,
        'full_name': full_name,
        'email_address': email,
    }
    resp = requests.post(url, post_data)
    return resp


def get_verify():
    url = testing['base_url'] + testing['port'] + 'verify'
    resp = requests.get(url)
    assert (resp.status_code == 200)
    return resp
