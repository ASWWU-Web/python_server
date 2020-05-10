import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.elections.candidate.candidate_subtests as candidate_subtests
import tests.aswwu.behaviors.elections.vote.vote_requests as vote_requests
import tests.aswwu.behaviors.elections.vote.vote_subtests as vote_subtests
import tests.aswwu.behaviors.auth.auth_subtests as auth_subtests
import tests.utils as utils
import tests.aswwu.data.paths as paths
import datetime as dt
import tests.aswwu.data.paths as paths
import json
import time
from tests.conftest import testing_server

POSITION_DATA = {
    'position': 'Senator',
    'election_type': 'aswwu',
    'active': 'True',
    'order': 1
}


def test_post_vote(testing_server):
    # user_data = election_subtests.POST_ELECTIONS_USER
    admin_session = election_subtests.create_elections_admin()
    election = election_subtests.assert_post_dynamic_election(admin_session)
    election_id = election['id']
    # position_resp = position_requests.post_position(admin_session, POSITION_DATA['position'], POSITION_DATA['election_type'],
    #                                            POSITION_DATA['active'], POSITION_DATA['order'])
    candidate_data, election_id, position_ids, user_data = candidate_subtests.create_candidates(admin_session, election)
    # pos_resp_data = json.loads(position_resp.text)
    # position_id = pos_resp_data['id']
    time.sleep(3)

    # users = utils.load_csv(paths.USERS_PATH)
    i = 0
    for candidate_id, candidate in candidate_data.items():
        user_session = auth_subtests.assert_verify_login(user_data[i])[1]
        i += 1
        print(candidate)
        vote = candidate['username']
        resp = vote_requests.post_vote(user_session, election_id, position_ids[1], vote)
        assert (resp.status_code == 201)
        resp_data = json.loads(resp.text)
        print(resp_data)
        vote_data = {'vote': vote, 'position': position_ids[1], 'election': election_id}
        vote_subtests.assert_vote_data(resp_data, vote_data)
