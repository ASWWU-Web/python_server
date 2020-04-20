import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.aswwu.behaviors.auth.auth_subtests as auth_subtests
import tests.aswwu.behaviors.elections.election.election_requests as election_requests
import tests.utils as utils
import tests.aswwu.data.paths as paths
import json
# from datetime import datetime, timedelta
import datetime as dt
from tests.conftest import testing_server

POST_ELECTIONS_USER = {
    'wwuid': '1234567',
    'full_name': 'John McJohn',
    'email': 'john.mcjohn@wallawalla.edu',
    'username': 'john.mcjohn',
    'roles': ['elections-admin']
}


def test_post_election(testing_server):
    session = _create_elections_admin()
    _create_elections(session)


def test_get_election(testing_server):
    session = _create_elections_admin()
    election_data = _create_elections(session)

    resp = election_requests.get_election()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['elections']

    for data in resp_data:
        election_subtests.assert_election_data(data, election_data[data['id']])


def test_get_current(testing_server):
    session = _create_elections_admin()
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
    session = _create_elections_admin()
    election_data = _create_elections(session)
    for key, election in election_data.items():
        resp = election_requests.get_specified_election(key)
        assert(resp.status_code == 200)
        election_subtests.assert_election_data(json.loads(resp.text), election)


def _create_elections_admin():
    session = auth_subtests.assert_verify_login(POST_ELECTIONS_USER)[1]
    auth_requests.post_roles(POST_ELECTIONS_USER['wwuid'], POST_ELECTIONS_USER['roles'])
    return session


def _create_elections(session):
    election_data = {}
    # Populate elections database
    elections = utils.load_csv(paths.ELECTIONS_PATH)
    for election in elections:
        resp_data = election_subtests.assert_post_election(session, election)
        election_data[resp_data['id']] = resp_data
    return election_data


