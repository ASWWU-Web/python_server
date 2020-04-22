import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import tests.aswwu.behaviors.elections.election.election_requests as election_requests
import json
import datetime as dt
from tests.conftest import testing_server


def test_post_election(testing_server):
    session = election_subtests.create_elections_admin()
    election_subtests.create_elections(session)


def test_get_election(testing_server):
    session = election_subtests.create_elections_admin()
    election_data = election_subtests.create_elections(session)

    resp = election_requests.get_election()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['elections']

    for data in resp_data:
        election_subtests.assert_election_data(data, election_data[data['id']])


def test_get_current(testing_server):
    session = election_subtests.create_elections_admin()
    dynamic_election = {
        'election_type': 'aswwu',
        'name': 'General Election Test',
        'max_votes': 2,
        'start': dt.datetime.strftime(dt.datetime.now() + dt.timedelta(hours=1), '%Y-%m-%d %H:%M:%S.%f'),
        'end': dt.datetime.strftime(dt.datetime.now() + dt.timedelta(days=1), '%Y-%m-%d %H:%M:%S.%f'),
        'show_results': dt.datetime.strftime(dt.datetime.now() + dt.timedelta(days=1), '%Y-%m-%d %H:%M:%S.%f'),
    }
    election = election_subtests.assert_post_election(session, dynamic_election)

    resp = election_requests.get_current()
    resp_data = json.loads(resp.text)
    assert (resp.status_code == 200)
    assert (dt.datetime.strptime(resp_data['end'], "%Y-%m-%d %H:%M:%S.%f") >= dt.datetime.now())
    election_subtests.assert_election_data(resp_data, election)


def test_get_specified_election(testing_server):
    session = election_subtests.create_elections_admin()
    election_data = election_subtests.create_elections(session)
    for key, election in election_data.items():
        resp = election_requests.get_specified_election(key)
        assert(resp.status_code == 200)
        election_subtests.assert_election_data(json.loads(resp.text), election)
