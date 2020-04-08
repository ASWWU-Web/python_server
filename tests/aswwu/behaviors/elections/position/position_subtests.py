import json
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
from tests.utils import load_csv
from tests.aswwu.data.paths import POSITIONS_PATH


def send_get_position(positions_data):
    resp = position_requests.get_position()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['positions']
    for data in resp_data:
        _verify_position_data(data, positions_data[data['id']])


def send_post_position():
    positions = load_csv(POSITIONS_PATH)
    positions_data = {}
    for position in positions:
        resp = position_requests.post_position(position['position'], position['election_type'], position['active'],
                                               position['order'])
        resp_data = json.loads(resp.text)
        assert (resp.status_code == 201)
        _verify_position_data(resp_data, position)
        positions_data[resp_data['id']] = resp_data
    return positions_data


def _verify_position_data(resp_data, position_data):
    assert (resp_data['position'] == position_data['position'])
    assert (resp_data['election_type'] == position_data['election_type'])
    assert (str(resp_data['active']) == str(position_data['active']))
    assert (str(resp_data['order']) == str(position_data['order']))
