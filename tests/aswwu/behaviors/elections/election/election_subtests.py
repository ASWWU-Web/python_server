import tests.aswwu.behaviors.elections.election.election_requests as election_requests
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.aswwu.behaviors.auth.auth_subtests as auth_subtests
import tests.aswwu.data.paths as paths
import tests.utils as utils
import datetime as dt
import json

POST_ELECTIONS_USER = {
    'wwuid': '1234567',
    'full_name': 'John McJohn',
    'email': 'john.mcjohn@wallawalla.edu',
    'username': 'john.mcjohn',
    'roles': ['elections-admin']
}
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

def assert_election_data(resp_data, election):
    assert (resp_data['election_type'] == election['election_type'])
    assert (resp_data['name'] == election['name'])
    assert (int(resp_data['max_votes']) == int(election['max_votes']))
    assert (resp_data['start'] == election['start'])
    assert (resp_data['end'] == election['end'])
    assert (resp_data['show_results'] == election['show_results'])


def assert_post_election(session, election):
    resp = election_requests.post_election(session, election['election_type'], election['name'], election['max_votes'],
                                           election['start'], election['end'], election['show_results'])
    resp_data = json.loads(resp.text)
    assert (resp.status_code == 201)
    assert_election_data(resp_data, election)
    return json.loads(resp.text)


def assert_post_dynamic_election(session):
    dynamic_election = {
        'election_type': 'aswwu',
        'name': 'General Election Test',
        'max_votes': 2,
        'start': dt.datetime.strftime(dt.datetime.now() + dt.timedelta(seconds=2), DATETIME_FORMAT),
        'end': dt.datetime.strftime(dt.datetime.now() + dt.timedelta(days=1), DATETIME_FORMAT),
        'show_results': dt.datetime.strftime(dt.datetime.now() + dt.timedelta(days=1), DATETIME_FORMAT),
    }
    election = assert_post_election(session, dynamic_election)
    resp = election_requests.get_current()
    resp_data = json.loads(resp.text)
    assert (resp.status_code == 200)
    assert (dt.datetime.strptime(resp_data['end'], DATETIME_FORMAT) >= dt.datetime.now())
    assert_election_data(resp_data, election)
    return resp_data


def create_elections_admin():
    session = auth_subtests.assert_verify_login(POST_ELECTIONS_USER)[1]
    auth_requests.post_roles(POST_ELECTIONS_USER['wwuid'], POST_ELECTIONS_USER['roles'])
    return session


def create_elections(session):
    election_data = {}
    # Populate elections database
    elections = utils.load_csv(paths.ELECTIONS_PATH)
    for election in elections:
        resp_data = assert_post_election(session, election)
        election_data[resp_data['id']] = resp_data
    return election_data


def add_hour_dt(dt_string):
    return dt.datetime.strftime(dt.datetime.strptime(dt_string, DATETIME_FORMAT) + dt.timedelta(hours=1), DATETIME_FORMAT)