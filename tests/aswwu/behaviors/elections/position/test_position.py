import tests.aswwu.behaviors.elections.position.position_utils as position_utils
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.elections.election.election_utils as election_utils
import json
from tests.conftest import testing_server


def test_post_position(testing_server):
    session = election_utils.create_elections_admin()
    position_utils.create_positions(session)


def test_get_position(testing_server):
    session = election_utils.create_elections_admin()
    position_data = position_utils.create_positions(session)

    resp = position_requests.get_position()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['positions']
    for data in resp_data:
        position_utils.assert_position_data(data, position_data[data['id']])


def test_put_specified_position(testing_server):
    session = election_utils.create_elections_admin()
    position_data = position_utils.create_positions(session)
    for key, value in position_data.items():
        updated_position_data = {
            'id': key,
            'position': value['position'] + '_updated',
            'election_type': 'senate' if value['election_type'] == 'aswwu' else 'aswwu',
            'active': value['active'] == 'True',
            'order': int(value['order']) + 1
        }
        resp = position_requests.put_specified_position(session, position_id=key,
                                                        position=updated_position_data['position'],
                                                        election_type=updated_position_data['election_type'],
                                                        active=updated_position_data['active'],
                                                        order=updated_position_data['order'])
        assert(resp.status_code == 200)
        position_utils.assert_position_data(json.loads(resp.text), updated_position_data)


def test_get_specified_position(testing_server):
    session = election_utils.create_elections_admin()
    position_data = position_utils.create_positions(session)
    for key, position in position_data.items():
        resp = position_requests.get_specified_position(key)
        assert (resp.status_code == 200)
        position_utils.assert_position_data(json.loads(resp.text), position)
