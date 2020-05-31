import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import json


def assert_position_data(resp_data, position_data):
    assert (resp_data['position'] == position_data['position'])
    assert (resp_data['election_type'] == position_data['election_type'])
    assert (str(resp_data['active']) == str(position_data['active']))
    assert (str(resp_data['order']) == str(position_data['order']))


def assert_create_positions(session, positions):
    """
    Populate database with positions
    :param session: user session with elections-admin privilege
    :param positions: list of data for position
    :return: dictionary with position data
    """
    position_data = []
    for position in positions:
        resp = position_requests.post_position(session,
                                               position['position'],
                                               position['election_type'],
                                               position['active'],
                                               position['order'])
        resp_data = json.loads(resp.text)
        assert (resp.status_code == 201)
        assert_position_data(resp_data, position)
        position_data.append(resp_data)
    return position_data
