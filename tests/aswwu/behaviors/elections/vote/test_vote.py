import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.elections.vote.vote_requests as vote_requests
import tests.aswwu.behaviors.elections.vote.vote_subtests as vote_subtests
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
    admin_session = election_subtests.create_elections_admin()
    election_id = election_subtests.assert_post_dynamic_election(admin_session)['id']
    position_resp = position_requests.post_position(admin_session, POSITION_DATA['position'],
                                                    POSITION_DATA['election_type'],
                                                    POSITION_DATA['active'], POSITION_DATA['order'])
    position_id = json.loads(position_resp.text)['id']
    vote_subtests.create_votes(admin_session, election_id, position_id)


def test_post_vote_candidates(testing_server):
    pass
    # response_txt = json.loads(response.text)['user']
    # response_txt['email'] = user['email']
    # user_data.append(response_txt)

    # resp = candidate_requests.post_candidate(session, election_id, position_ids[count % 2], user['username'],
    #                                          user['full_name'])
    # resp_data = json.loads(resp.text)
    # candidate = {'position': position_ids[count % 2], 'username': user['username'],
    #              'display_name': user['full_name']}
    # assert (resp.status_code == 201)
    # assert_candidate_data(resp_data, candidate)
    # candidate_data[resp_data['id']] = resp_data

    # users = utils.load_csv(paths.USERS_PATH)
    # i = 0
    # for candidate_id, candidate in candidate_data.items():
    #     user_session = auth_subtests.assert_verify_login(user_data[i])[1]
    #     i += 1
    #     print(candidate)
    #     vote = candidate['username']
    #     resp = vote_requests.post_vote(user_session, election_id, position_ids[1], vote)
    #     assert (resp.status_code == 201)
    #     resp_data = json.loads(resp.text)
    #     print(resp_data)
    #     vote_data = {'vote': vote, 'position': position_ids[1], 'election': election_id}
    #     vote_subtests.assert_vote_data(resp_data, vote_data)


def test_get_vote(testing_server):
    admin_session = election_subtests.create_elections_admin()
    election_id = election_subtests.assert_post_dynamic_election(admin_session)['id']
    position_resp = position_requests.post_position(admin_session, POSITION_DATA['position'],
                                                    POSITION_DATA['election_type'],
                                                    POSITION_DATA['active'], POSITION_DATA['order'])
    position_id = json.loads(position_resp.text)['id']
    vote_data = vote_subtests.create_votes(admin_session, election_id, position_id)
    users = utils.load_csv(paths.USERS_PATH)

    for count, user in enumerate(users):
        user_session = auth_subtests.assert_verify_login(user)[1]
        resp = vote_requests.get_vote(user_session, position_id, user['username'])
        assert (resp.status_code == 200)
        resp_text = json.loads(resp.text)['votes']
        for vote in resp_text:
            vote_subtests.assert_vote_data(vote, vote_data[user['username']])
