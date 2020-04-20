import tests.aswwu.behaviors.elections.position.position_subtests as position_subtests
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.auth.auth_subtests as auth_subtests
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.utils as utils
from tests.conftest import testing_server
import tests.aswwu.data.paths as paths
import json

POST_ELECTIONS_USER = {
    'wwuid': '1234567',
    'full_name': 'John McJohn',
    'email': 'john.mcjohn@wallawalla.edu',
    'username': 'john.mcjohn',
    'roles': ['elections-admin']
}


def test_post_position(testing_server):
    session = _create_elections_admin()

    positions = utils.load_csv(paths.POSITIONS_PATH)
    for position in positions:
        resp = position_requests.post_position(session, position['position'], position['election_type'], position['active'],
                                               position['order'])
        resp_data = json.loads(resp.text)
        assert (resp.status_code == 201)
        position_subtests.verify_position_data(resp_data, position)


def test_get_position(testing_server):
    session = _create_elections_admin()
    position_data = {}
    positions = utils.load_csv(paths.POSITIONS_PATH)
    for position in positions:
        resp = position_requests.post_position(session, position['position'], position['election_type'], position['active'],
                                               position['order'])
        resp_data = json.loads(resp.text)
        assert (resp.status_code == 201)
        position_subtests.verify_position_data(resp_data, position)
        position_data[resp_data['id']] = resp_data

    resp = position_requests.get_position()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['positions']
    for data in resp_data:
        position_subtests.verify_position_data(data, position_data[data['id']])


def _create_elections_admin():
    session = auth_subtests.assert_verify_login(POST_ELECTIONS_USER)[1]
    auth_requests.post_roles(POST_ELECTIONS_USER['wwuid'], POST_ELECTIONS_USER['roles'])
    return session


def _create_positions(session):
    positions = utils.load_csv(paths.POSITIONS_PATH)
    for position in positions:
        resp = position_requests.post_position(session, position['position'], position['election_type'],
                                               position['active'],
                                               position['order'])
        resp_data = json.loads(resp.text)
        assert (resp.status_code == 201)
        position_subtests.verify_position_data(resp_data, position)
        position_data[resp_data['id']] = resp_data
