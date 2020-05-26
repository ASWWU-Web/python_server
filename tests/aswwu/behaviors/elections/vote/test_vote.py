import tests.aswwu.behaviors.elections.election.election_utils as election_utils
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.elections.vote.vote_requests as vote_requests
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.aswwu.behaviors.elections.vote.vote_utils as vote_utils
import tests.aswwu.behaviors.auth.auth_subtests as auth_subtests
import tests.aswwu.data.paths as paths
import tests.utils as utils
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
    admin_session = election_utils.create_elections_admin()[1]
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']
    position_resp = position_requests.post_position(admin_session, POSITION_DATA['position'],
                                                    POSITION_DATA['election_type'],
                                                    POSITION_DATA['active'], POSITION_DATA['order'])
    position_id = json.loads(position_resp.text)['id']
    vote_utils.create_votes(election_id, position_id)


def test_post_vote_candidates(testing_server):
    """
    Test voting for candidates
    :param testing_server:
    """
    pass


def test_get_vote(testing_server):
    admin_session = election_utils.create_elections_admin()[1]
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']
    position_resp = position_requests.post_position(admin_session, POSITION_DATA['position'],
                                                    POSITION_DATA['election_type'],
                                                    POSITION_DATA['active'], POSITION_DATA['order'])
    position_id = json.loads(position_resp.text)['id']
    vote_data = vote_utils.create_votes(election_id, position_id)
    users = utils.load_csv(paths.USERS_PATH)

    for count, user in enumerate(users):
        user_session = auth_subtests.assert_verify_login(user)[1]
        resp = vote_requests.get_vote(user_session, position_id, user['username'])
        assert (resp.status_code == 200)
        resp_text = json.loads(resp.text)['votes']
        for vote in resp_text:
            vote_utils.assert_vote_data(vote, vote_data[user['username']])


def test_get_specified_vote(testing_server):
    # create admin session
    admin_session = election_utils.create_elections_admin()[1]

    # create dynamic election
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']

    # create generic position
    position_resp = position_requests.post_position(admin_session, 'President', 'aswwu', 'True', '1')
    position_id = json.loads(position_resp.text)['id']

    # wait for election to open
    time.sleep(3)

    # post votes in election
    users = utils.load_csv(paths.USERS_PATH)

    for user in users:
        # login as user
        auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
        user_session = auth_subtests.assert_verify_login(user)[1]

        # create vote
        vote_resp = vote_requests.post_vote(user_session,
                                            election=election_id,
                                            position=position_id,
                                            vote=user['username'])
        vote_resp_data = json.loads(vote_resp.text)
        assert (vote_resp.status_code == 201)

        # GET specified vote
        specified_vote_resp = vote_requests.get_specified_vote(user_session, vote_resp_data['id'])
        assert (specified_vote_resp.status_code == 200)
        specified_vote_resp_data = json.loads(specified_vote_resp.text)
        utils.assert_is_equal_sub_dict(vote_resp_data, specified_vote_resp_data)


def test_put_specified_vote(testing_server):
    # create user to act as replacement vote
    new_user = {
        'wwuid': '9999999',
        'username': 'bob.dylan',
        'full_name': 'Bob Dylan',
        'email': 'bob.dylan@wallawalla.edu'
    }
    auth_subtests.assert_verify_login(new_user)

    # create admin session
    admin_session = election_utils.create_elections_admin()[1]

    # create dynamic election
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']

    # create generic position
    position_resp = position_requests.post_position(admin_session, 'President', 'aswwu', 'True', '1')
    position_id = json.loads(position_resp.text)['id']

    # wait for election to open
    time.sleep(2)

    # post votes in election
    users = utils.load_csv(paths.USERS_PATH)

    for user in users:
        # login as user
        auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
        user_session = auth_subtests.assert_verify_login(user)[1]

        # create vote
        vote_resp = vote_requests.post_vote(user_session,
                                            election=election_id,
                                            position=position_id,
                                            vote=user['username'])
        vote_resp_data = json.loads(vote_resp.text)
        assert (vote_resp.status_code == 201)

        # update vote by changing 'vote' field
        updated_vote_data = {
            'id': vote_resp_data['id'],
            'election': vote_resp_data['election'],
            'position': vote_resp_data['position'],
            'vote': new_user['username'],
            'username': user['username']
        }
        updated_vote_resp = vote_requests.put_specified_vote(user_session,
                                                             vote_id=updated_vote_data['id'],
                                                             election_id=updated_vote_data['election'],
                                                             position_id=updated_vote_data['position'],
                                                             vote=updated_vote_data['vote'],
                                                             user_username=updated_vote_data['username'])
        assert (updated_vote_resp.status_code == 200)
        updated_vote_resp_data = json.loads(updated_vote_resp.text)
        utils.assert_is_equal_sub_dict(updated_vote_data, updated_vote_resp_data)


def test_delete_specified_vote(testing_server):
    # create admin session
    admin_session = election_utils.create_elections_admin()[1]

    # create dynamic election
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']

    # create generic position
    position_resp = position_requests.post_position(admin_session, 'President', 'aswwu', 'True', '1')
    position_id = json.loads(position_resp.text)['id']

    # wait for election to open
    time.sleep(2)

    # post votes in election
    users = utils.load_csv(paths.USERS_PATH)
    for user in users:
        # login as user
        auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
        user_session = auth_subtests.assert_verify_login(user)[1]

        # create vote
        vote_resp = vote_requests.post_vote(user_session,
                                            election=election_id,
                                            position=position_id,
                                            vote=user['username'])
        vote_resp_data = json.loads(vote_resp.text)
        assert (vote_resp.status_code == 201)

        # delete vote
        del_vote_resp = vote_requests.delete_specified_vote(admin_session, vote_resp_data['id'])
        assert(del_vote_resp.status_code == 204)

        # assert vote no longer exists
        specified_vote_resp = vote_requests.get_specified_vote(user_session, vote_resp_data['id'])
        assert (specified_vote_resp.status_code == 404)
