import requests
import json
from tests.utils import askanything, askanthingvote, edit, gen_askanythingvotes, gen_askanythings


def test_get_No_Data(testing_server):

    expected_data = []

    url = "http://127.0.0.1:8888/askanything/view"
    resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_get_data(testing_server, peopledb_conn):
    expected_data = [{
        "votes": 0,
        "reviewed": True,
        "question": "Something_0",
        "authorized": True,
        "has_voted": False,
        "question_id": "0",
    }, {
        "votes": 0,
        "reviewed": True,
        "question": "Something_1",
        "authorized": True,
        "has_voted": False,
        "question_id": "1",
    }, {
        "votes": 0,
        "reviewed": True,
        "question": "Something_2",
        "authorized": True,
        "has_voted": False,
        "question_id": "2",
    }]

    with askanything(peopledb_conn, list(gen_askanythings(number=3))):
        url = "http://127.0.0.1:8888/askanything/view"
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_get_data_with_votes(testing_server, peopledb_conn):
    expected_data = [{
        "votes": 1,
        "reviewed": True,
        "question": "Something_0",
        "authorized": True,
        "has_voted": False,
        "question_id": "0",
    }, {
        "votes": 1,
        "reviewed": True,
        "question": "Something_1",
        "authorized": True,
        "has_voted": False,
        "question_id": "1",
    }, {
        "votes": 1,
        "reviewed": True,
        "question": "Something_2",
        "authorized": True,
        "has_voted": False,
        "question_id": "2",
    }]

    data = list(
        edit(
            gen_askanythingvotes(number=3), {
                0: {
                    'question_id': 0
                },
                1: {
                    'question_id': 1
                },
                2: {
                    'question_id': 2
                }
            }))

    with askanything(
            peopledb_conn, list(gen_askanythings(number=3))), askanthingvote(
                peopledb_conn, data):
        url = "http://127.0.0.1:8888/askanything/view"
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_get_not_authorized(testing_server, peopledb_conn):
    expected_data = [{
        "votes": 1,
        "reviewed": True,
        "question": "Something_1",
        "authorized": True,
        "has_voted": False,
        "question_id": "1",
    }]

    anythings = list(
        edit(
            gen_askanythings(number=3), {
                0: {'authorized': False},
                2: {'authorized': False}
            }))

    votes = list(
        edit(
            gen_askanythingvotes(number=3), {
                0: {'question_id': 0},
                1: {'question_id': 1},
                2: {'question_id': 2}
            }))

    with askanything(peopledb_conn, anythings), askanthingvote(peopledb_conn, votes):
        url = "http://127.0.0.1:8888/askanything/view"
        resp = requests.get(url)

    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_get_no_reviewed(testing_server, peopledb_conn):
    expected_data = [{
        "votes": 1,
        "reviewed": True,
        "question": "Something_1",
        "authorized": True,
        "has_voted": False,
        "question_id": "1",
    }]

    anythings = list(
        edit(
            gen_askanythings(number=3), {
                0: {'reviewed': False},
                2: {'reviewed': False}
            }))

    votes = list(
        edit(
            gen_askanythingvotes(number=3), {
                0: {'question_id': 0},
                1: {'question_id': 1},
                2: {'question_id': 2}
            }))

    with askanything(peopledb_conn, anythings), askanthingvote(peopledb_conn, votes):
        url = "http://127.0.0.1:8888/askanything/view"
        resp = requests.get(url)

    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)

def test_get_user_voted(testing_server, peopledb_conn):
    expected_data = [{
        "votes": 1,
        "reviewed": True,
        "question": "Something_0",
        "authorized": True,
        "has_voted": True,
        "question_id": "0",
    }]

    votes = list(
        edit(
            gen_askanythingvotes(number=1), {
                0: {'question_id': 0, 'voter': 'ryan.rabello'}
            }))

    with askanything(peopledb_conn, list(gen_askanythings(number=1))), askanthingvote(peopledb_conn, votes):
        url = "http://127.0.0.1:8888/askanything/view"
        resp = requests.get(url)

    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)
