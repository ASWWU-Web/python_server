# /senate_election/showall
# /senate_election/vote/(.*)
# /senate_election/livefeed

import requests
import json
from tests.utils import election, edit, gen_elections
from datetime import datetime


def test_no_data(testing_server):
    expected_data = {
        "results": []
    }

    url = "http://127.0.0.1:8888/senate_election/showall"
    resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_data(testing_server, electiondb_conn):
    expected_data = {
        "results": [
            {
                "wwuid": "9000000",
                "district": "district_0",
                "candidate_two": "person_B0",
                "sm_two": "person_D0",
                "candidate_one": "person_A0",
                "updated_at": "2000-01-01 00:00:00",
                "new_department": "department_0",
                "sm_one": "person_C0"
            }, {
                "wwuid": "9000001",
                "district": "district_1",
                "candidate_two": "person_B1",
                "sm_two": "person_D1",
                "candidate_one": "person_A1",
                "updated_at": "2000-01-01 00:00:00",
                "new_department": "department_1",
                "sm_one": "person_C1"
            }, {
                "wwuid": "9000002",
                "district": "district_2",
                "candidate_two": "person_B2",
                "sm_two": "person_D2",
                "candidate_one": "person_A2",
                "updated_at": "2000-01-01 00:00:00",
                "new_department": "department_2",
                "sm_one": "person_C2"
            }
        ]
    }

    with election(electiondb_conn, list(gen_elections(number=3))):
        url = "http://127.0.0.1:8888/senate_election/showall"
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)
