import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import tests.aswwu.behaviors.elections.candidate.candidate_requests as candidate_requests
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.data.paths as paths
import tests.utils as utils
import json

# TODO probs don't need this here
POSITION_DATA = {
    'position': 'Senator',
    'election_type': 'aswwu',
    'active': 'True',
    'order': 1
}


def create_candidates():
    candidate_data = {}
    session = election_subtests.create_elections_admin()
    election_id = election_subtests.assert_post_dynamic_election(session)['id']
    position_resp = position_requests.post_position(session, POSITION_DATA['position'],
                                                    POSITION_DATA['election_type'],
                                                    POSITION_DATA['active'], POSITION_DATA['order'])
    position_id = json.loads(position_resp.text)['id']
    users = utils.load_csv(paths.USERS_PATH)
    for user in users:
        resp = candidate_requests.post_candidate(session, election_id, position_id, user['username'], user['full_name'])
        resp_data = json.loads(resp.text)
        candidate = {'position': position_id, 'username': user['username'], 'display_name': user['full_name']}
        assert (resp.status_code == 201)
        assert_candidate_data(resp_data, candidate)
        candidate_data[resp_data['id']] = resp_data
    return candidate_data, election_id


def assert_candidate_data(resp, candidate):
    assert(resp['position'] == candidate['position'])
    assert(resp['username'] == candidate['username'])
    assert(resp['display_name'] == candidate['display_name'])
