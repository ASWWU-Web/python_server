import json
import csv
# from tests.conftest import testing_server
from tests.aswwu.requests import verify
import os


def test_saml_create_user():

    for i in range(0, NUM_USERS):
        saml_create_single_user()


def saml_create_single_user():
    resp = verify.post_verify('1234567', 'john doe', 'john.doe@wallawalla.edu')

    resp = requests.post(url, post_data)
    resp_text = json.loads(resp.text)
    assert (resp.status_code == 200)
    assert (resp_text['token'].split('|')[0] == '1234567')
    assert (resp_text['user']['username'] == '1234567.testemail')
    assert (resp_text['user']['wwuid'] == '1234567')
    assert (resp_text['user']['roles'] == 'None')
    assert (resp_text['user']['status'] == 'Student')
    assert (resp_text['user']['full_name'] == '1234567 test full name')

def test_load_users():
    load_users('tests/aswwu/behaviors/users.csv')

def load_users(users_file):
    users_list = None
    with open(users_file) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        users_list = [{
            'wwuid': row[0],
            'full_name': row[1],
            'email': row[2]
        } for row in csv_reader]
    return

