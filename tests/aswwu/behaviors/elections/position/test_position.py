import tests.aswwu.behaviors.elections.position.position_utils as position_utils
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.elections.election.election_utils as election_utils
from tests.aswwu.data.positions import POSITIONS
import json
from tests.conftest import testing_server


def test_post_position(testing_server):
    session = election_utils.create_elections_admin()[1]
    position_utils.assert_create_positions(session, POSITIONS)


def test_get_position(testing_server):
    session = election_utils.create_elections_admin()[1]
    positions = position_utils.assert_create_positions(session, POSITIONS)
    position_data = {}

    for position in positions:
        position_data[position['id']] = position

    resp = position_requests.get_position()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['positions']
    for data in resp_data:
        position_utils.assert_position_data(data, position_data[data['id']])


def test_put_specified_position(testing_server):
    session = election_utils.create_elections_admin()[1]
    position_data = position_utils.assert_create_positions(session, POSITIONS)
    for position in position_data:
        updated_position_data = {
            'id': position['id'],
            'position': position['position'] + '_updated',
            'election_type': 'senate' if position['election_type'] == 'aswwu' else 'aswwu',
            'active': position['active'] == 'True',
            'order': int(position['order']) + 1
        }
        resp = position_requests.put_specified_position(session, position_id=position['id'],
                                                        position=updated_position_data['position'],
                                                        election_type=updated_position_data['election_type'],
                                                        active=updated_position_data['active'],
                                                        order=updated_position_data['order'])
        assert(resp.status_code == 200)
        position_utils.assert_position_data(json.loads(resp.text), updated_position_data)


def test_get_specified_position(testing_server):
    session = election_utils.create_elections_admin()[1]
    position_data = position_utils.assert_create_positions(session, POSITIONS)
    for position in position_data:
        resp = position_requests.get_specified_position(position['id'])
        assert (resp.status_code == 200)
        position_utils.assert_position_data(json.loads(resp.text), position)
