import json
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
from tests.utils import load_csv
from tests.aswwu.data.paths import POSITIONS_PATH


def send_get_position():
    resp = position_requests.get_position()
    resp_text = json.loads(resp.text)
    assert(resp.status_code == 200)


def send_post_position():
    positions = load_csv(POSITIONS_PATH)
    for position in positions:
        resp = position_requests.post_position(position['position'], position['election_type'], position['active'],
                                                position['order'])
        resp_text = json.loads(resp.text)
        assert (resp.status_code == 201)
        assert(resp_text['position'] == position['position'])
        assert(resp_text['election_type'] == position['election_type'])
        assert(str(resp_text['active']) == position['active'])
        assert(str(resp_text['order']) == position['order'])