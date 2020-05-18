import tests.aswwu.behaviors.elections.election.election_utils as election_utils
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.elections.vote.vote_requests as vote_requests
import tests.aswwu.behaviors.elections.vote.vote_utils as vote_utils
import tests.aswwu.behaviors.auth.auth_subtests as auth_subtests
import tests.aswwu.data.paths as paths
import tests.utils as utils
import json
from tests.conftest import testing_server

POSITION_DATA = {
    'position': 'Senator',
    'election_type': 'aswwu',
    'active': 'True',
    'order': 1
}


def test_post_vote(testing_server):
    admin_session = election_utils.create_elections_admin()
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']
    position_resp = position_requests.post_position(admin_session, POSITION_DATA['position'],
                                                    POSITION_DATA['election_type'],
                                                    POSITION_DATA['active'], POSITION_DATA['order'])
    position_id = json.loads(position_resp.text)['id']
    vote_utils.create_votes(admin_session, election_id, position_id)


def test_post_vote_candidates(testing_server):
    pass


def test_get_vote(testing_server):
    admin_session = election_utils.create_elections_admin()
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']
    position_resp = position_requests.post_position(admin_session, POSITION_DATA['position'],
                                                    POSITION_DATA['election_type'],
                                                    POSITION_DATA['active'], POSITION_DATA['order'])
    position_id = json.loads(position_resp.text)['id']
    vote_data = vote_utils.create_votes(admin_session, election_id, position_id)
    users = utils.load_csv(paths.USERS_PATH)

    for count, user in enumerate(users):
        user_session = auth_subtests.assert_verify_login(user)[1]
        resp = vote_requests.get_vote(user_session, position_id, user['username'])
        assert (resp.status_code == 200)
        resp_text = json.loads(resp.text)['votes']
        for vote in resp_text:
            vote_utils.assert_vote_data(vote, vote_data[user['username']])
