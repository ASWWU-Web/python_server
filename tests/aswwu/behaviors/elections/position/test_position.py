import tests.aswwu.behaviors.elections.position.position_subtests as position_subtests
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import json
from tests.conftest import testing_server


def test_post_position(testing_server):
    session = election_subtests.create_elections_admin()
    position_subtests.create_positions(session)


def test_get_position(testing_server):
    session = election_subtests.create_elections_admin()
    position_data = position_subtests.create_positions(session)

    resp = position_requests.get_position()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['positions']
    for data in resp_data:
        position_subtests.assert_position_data(data, position_data[data['id']])


def test_put_specified_position(testing_server):
    session = election_subtests.create_elections_admin()
    position_data = position_subtests.create_positions(session)
    for key, value in position_data.items():
        updated_position_data = {
            'id': key,
            'position': value['position'] + '_updated',
            'election_type': 'senate' if value['election_type'] == 'aswwu' else 'aswwu',
            'active': value['active'] == 'True',
            'order': int(value['order']) + 1
        }
        resp = position_requests.put_specified_position(session, key, obj_data=updated_position_data)
        assert(resp.status_code == 200)
        print(updated_position_data)
        position_subtests.assert_position_data(json.loads(resp.text), updated_position_data)


def test_get_specified_position(testing_server):
    session = election_subtests.create_elections_admin()
    position_data = position_subtests.create_positions(session)
    for key, position in position_data.items():
        resp = position_requests.get_specified_position(key)
        assert (resp.status_code == 200)
        position_subtests.assert_position_data(json.loads(resp.text), position)