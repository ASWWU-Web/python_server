import requests
import json
from tests.utils import askanything, askanthingvote


def test_No_Data(testing_server):

    expected_data = []

    url = "http://127.0.0.1:8888/askanything/view"
    resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_data(testing_server, peopledb_conn):
    expected_data = [{
        u"votes": 0,
        u"reviewed": True,
        u"question": u"Something",
        u"authorized": True,
        u"has_voted": False,
        u"question_id": u"1",
    }, {
        u"votes": 0,
        u"reviewed": True,
        u"question": u"Something Else",
        u"authorized": True,
        u"has_voted": False,
        u"question_id": u"2",
    }, {
        u"votes": 0,
        u"reviewed": True,
        u"question": u"Something More",
        u"authorized": True,
        u"has_voted": False,
        u"question_id": u"3",
    }]

    with askanything(peopledb_conn):
        url = "http://127.0.0.1:8888/askanything/view"
        resp = requests.get(url)
        assert (resp.status_code == 200)
        assert (json.loads(resp.text) == expected_data)


def test_data_with_votes(testing_server, peopledb_conn):
    expected_data = [{
        u"votes": 1,
        u"reviewed": True,
        u"question": u"Something",
        u"authorized": True,
        u"has_voted": True,
        u"question_id": u"1",
    }, {
        u"votes": 1,
        u"reviewed": True,
        u"question": u"Something Else",
        u"authorized": True,
        u"has_voted": True,
        u"question_id": u"2",
    }, {
        u"votes": 1,
        u"reviewed": True,
        u"question": u"Something More",
        u"authorized": True,
        u"has_voted": True,
        u"question_id": u"3",
    }]

    with askanything(peopledb_conn), askanthingvote(peopledb_conn):
        url = "http://127.0.0.1:8888/askanything/view"
        resp = requests.get(url)
        assert (resp.status_code == 200)
        assert (json.loads(resp.text) == expected_data)
