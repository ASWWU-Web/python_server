import tests.aswwu.behaviors.elections.vote.vote_requests as vote_requests
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.aswwu.behaviors.auth.auth_subtests as auth_subtests
from tests.aswwu.data.users import USERS
import json
import time


def assert_create_votes(election, positions):
    """
    Populate test database with votes
    :param election: election object to create votes for
    :param positions: list of positions to vote for
    :return: dictionary of vote data
    """
    vote_data = {}
    election_id = election['id']

    # only add position ids in election
    position_ids = []
    for i, position in enumerate(positions):
        if position['election_type'] == election['election_type']:
            position_ids.append(position['id'])

    # Number of votable positions
    num_positions = len(position_ids)

    for i, user in enumerate(USERS):
        position_id = position_ids[i % num_positions]
        auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
        user_session = auth_subtests.assert_verify_login(user)[1]
        vote = {
            'election': election_id,
            'position': position_id,
            "vote": user['username']
        }
        resp = vote_requests.post_vote(user_session, election=election_id, position=position_id, vote=user['username'])
        resp_text = json.loads(resp.text)
        assert (resp.status_code == 201)
        assert_vote_data(resp_text, vote)
        vote_data[resp_text['username']] = resp_text
    return vote_data


def assert_vote_data(resp, vote):
    assert (resp['election'] == vote['election'])
    assert (resp['position'] == vote['position'])
    assert (resp['vote'] == vote['vote'])
