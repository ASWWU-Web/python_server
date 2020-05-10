import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.data.paths as paths
import tests.utils as utils
import json


def send_get_specified_position(position_id):
    pass


def assert_position_data(resp_data, position_data):
    assert (resp_data['position'] == position_data['position'])
    assert (resp_data['election_type'] == position_data['election_type'])
    assert (str(resp_data['active']) == str(position_data['active']))
    assert (str(resp_data['order']) == str(position_data['order']))


def create_positions(session):
    position_data = {}
    positions = utils.load_csv(paths.POSITIONS_PATH)
    for position in positions:
        resp = position_requests.post_position(session, position['position'], position['election_type'],
                                               position['active'],
                                               position['order'])
        resp_data = json.loads(resp.text)
        print(resp_data)
        assert (resp.status_code == 201)
        assert_position_data(resp_data, position)
        position_data[resp_data['id']] = resp_data
    return position_data
