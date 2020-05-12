import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import tests.aswwu.behaviors.elections.candidate.candidate_requests as candidate_requests
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.aswwu.data.paths as paths
import tests.utils as utils
import json

# TODO probs don't need this here
POSITION_DATA = [
    {
        'position': 'EVP',
        'election_type': 'aswwu',
        'active': 'True',
        'order': 2},
    {
        'position': 'President',
        'election_type': 'aswwu',
        'active': 'True',
        'order': 2
    }
]


def create_candidates(session, election=None):
    candidate_data = {}
    if not election:
        election_id = election_subtests.assert_post_dynamic_election(session)['id']
    else:
        election_id = election['id']
    position_resp1 = position_requests.post_position(session, obj_data=POSITION_DATA[0])
    position_resp2 = position_requests.post_position(session, obj_data=POSITION_DATA[1])

    position_ids = [json.loads(position_resp1.text)['id'], json.loads(position_resp2.text)['id']]

    users = utils.load_csv(paths.USERS_PATH)
    for count, user in enumerate(users):
        response = auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
        response_txt = json.loads(response.text)['user']
        response_txt['email'] = user['email']
        resp = candidate_requests.post_candidate(session, election_id, position_ids[count % 2], user['username'], user['full_name'])
        resp_data = json.loads(resp.text)
        candidate = {'position': position_ids[count % 2], 'username': user['username'], 'display_name': user['full_name']}
        assert (resp.status_code == 201)
        assert_candidate_data(resp_data, candidate)
        candidate_data[resp_data['id']] = resp_data
    return candidate_data, election_id, position_ids


def assert_candidate_data(resp, candidate):
    assert(resp['position'] == candidate['position'])
    assert(resp['username'] == candidate['username'])
    assert(resp['display_name'] == candidate['display_name'])
