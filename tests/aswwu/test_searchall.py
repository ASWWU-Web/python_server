import requests
import json
from tests.conftest import testing_server
from settings import keys


def test_search_all(testing_server):
    expected_data = {
        "results": []
    }

    url = 'http://127.0.0.1:8888/search/all'
    resp = requests.get(url)

    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_saml_request(testing_server):
    url = 'http://127.0.0.1:8888/verify'
    post_data = {
        'secret_key': keys["samlEndpointKey"],
        'employee_id': '1234567',
        'full_name': '1234567 test full name',
        'email_address': '1234567.testemail@wallawalla.edu',
    }
    resp = requests.post(url, post_data)
    resp_text = json.loads(resp.text)
    assert (resp.status_code == 200)
    assert (resp_text['token'].split('|')[0] == '1234567')
    assert (resp_text['user']['username'] == '1234567.testemail')
    assert (resp_text['user']['wwuid'] == '1234567')
    assert (resp_text['user']['roles'] == 'None')
    assert (resp_text['user']['status'] == 'Student')
    assert (resp_text['user']['full_name'] == '1234567 test full name')
