import requests
from settings import keys, testing


VERIFY_URL = testing['base_url'] + ':' + str(testing['port']) + '/' + 'verify'


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
