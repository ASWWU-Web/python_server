import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import tests.aswwu.behaviors.elections.vote.vote_requests as vote_requests
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.aswwu.behaviors.auth.auth_subtests as auth_subtests
import tests.utils as utils
import tests.aswwu.data.paths as paths
import json
import time

POSITION_DATA = {
    'position': 'Senator',
    'election_type': 'aswwu',
    'active': 'True',
    'order': 1
}

def create_votes(session, election_id, position_id):
    time.sleep(3)
    vote_data = {}

    users = utils.load_csv(paths.USERS_PATH)
    for count, user in enumerate(users):
        auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
        user_session = auth_subtests.assert_verify_login(user)[1]
        vote = {
            'election': election_id,
            'position': position_id,
            "vote": user['username']
        }
        resp = vote_requests.post_vote(user_session, obj_data=vote)
        resp_text = json.loads(resp.text)
        assert (resp.status_code == 201)
        assert_vote_data(resp_text, vote)
        vote_data[resp_text['username']] = resp_text
    return vote_data


def assert_vote_data(resp, vote):
    assert (resp['election'] == vote['election'])
    assert (resp['position'] == vote['position'])
    assert (resp['vote'] == vote['vote'])