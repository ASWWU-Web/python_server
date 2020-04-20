import json
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
from tests.utils import load_csv
from tests.aswwu.data.paths import POSITIONS_PATH


def send_post_position(session):
    resp = position_requests.post_position(session, position['position'], position['election_type'], position['active'],
                                           position['order'])
    resp_data = json.loads(resp.text)
    assert (resp.status_code == 201)
    position_subtests.verify_position_data(resp_data, position)



    positions = load_csv(POSITIONS_PATH)
    positions_data = {}
    for position in positions:
        resp = position_requests.post_position(position['position'], position['election_type'], position['active'],
                                               position['order'])
        resp_data = json.loads(resp.text)
        assert (resp.status_code == 201)
        verify_position_data(resp_data, position)
        positions_data[resp_data['id']] = resp_data
    return positions_data


def send_get_specified_position(position_id):
    pass


def verify_position_data(resp_data, position_data):
    assert (resp_data['position'] == position_data['position'])
    assert (resp_data['election_type'] == position_data['election_type'])
    assert (str(resp_data['active']) == str(position_data['active']))
    assert (str(resp_data['order']) == str(position_data['order']))
