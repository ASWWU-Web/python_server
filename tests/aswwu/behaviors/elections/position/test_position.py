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


def test_put_position(testing_server):
    session = election_subtests.create_elections_admin()
    position_data = position_subtests.create_positions(session)
    for key, value in position_data.items():
        resp = position_requests.put_specified_position(session, key, value['position'], value['election_type'], value['active'], value['order'])
        assert(resp.status_code == 200)
        resp_data = json.loads(resp.text)
        position_subtests.assert_position_data(resp_data, value)
