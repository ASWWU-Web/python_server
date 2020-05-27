import tests.aswwu.behaviors.elections.ballot.ballot_requests as ballot_requests
import tests.aswwu.behaviors.elections.election.election_utils as election_utils
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.utils as utils
import tests.aswwu.data.paths as paths
import json
import time
from tests.conftest import testing_server


def test_post_ballot(testing_server):
    # create admin session
    user_data, admin_session = election_utils.create_elections_admin()
    admin_user_data = user_data['user']

    # create dynamic election
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']

    # create generic position
    position_resp = position_requests.post_position(admin_session, 'President', 'aswwu', 'True', '1')
    position_id = json.loads(position_resp.text)['id']

    # wait for election to open
    time.sleep(2)

    users = utils.load_csv(paths.USERS_PATH)
    for user in users:
        # login as user
        auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])

        ballot_resp = ballot_requests.post_ballot(user_session=admin_session,
                                                  election_id=election_id,
                                                  position_id=position_id,
                                                  student_id=user['wwuid'],
                                                  vote=user['username'])
        expected_ballot_resp_data = {
            'election': election_id,
            'position': position_id,
            'vote': user['username'],
            'student_id': user['wwuid'],
            'manual_entry': admin_user_data['username']
        }
        assert (ballot_resp.status_code == 201)
        ballot_resp_data = json.loads(ballot_resp.text)
        utils.assert_is_equal_sub_dict(expected=expected_ballot_resp_data, actual=ballot_resp_data)


def test_get_ballot(testing_server):
    # create admin session
    user_data, admin_session = election_utils.create_elections_admin()
    admin_user_data = user_data['user']

    # create dynamic election
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']

    # create generic position
    position_resp = position_requests.post_position(admin_session, 'President', 'aswwu', 'True', '1')
    position_id = json.loads(position_resp.text)['id']

    # wait for election to open
    time.sleep(2)

    # dictionary to store data from post request
    ballot_data = {}

    users = utils.load_csv(paths.USERS_PATH)
    for user in users:
        # login as user
        auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])

        ballot_post_resp = ballot_requests.post_ballot(user_session=admin_session,
                                                  election_id=election_id,
                                                  position_id=position_id,
                                                  student_id=user['wwuid'],
                                                  vote=user['username'])
        ballot_resp_data = json.loads(ballot_post_resp.text)
        ballot_data[ballot_resp_data['id']] = ballot_resp_data

    ballot_get_resp = ballot_requests.get_ballot(admin_session, election_id)
    assert (ballot_get_resp.status_code == 200)
    ballot_get_resp_data = json.loads(ballot_get_resp.text)['ballots']

    for ballot in ballot_get_resp_data:
        utils.assert_is_equal_sub_dict(ballot_data[ballot['id']], ballot)


def test_get_specified_ballot(testing_server):
    # create admin session
    user_data, admin_session = election_utils.create_elections_admin()
    admin_user_data = user_data['user']

    # create dynamic election
    election_id = election_utils.assert_post_dynamic_election(admin_session)['id']

    # create generic position
    position_resp = position_requests.post_position(admin_session, 'President', 'aswwu', 'True', '1')
    position_id = json.loads(position_resp.text)['id']

    # wait for election to open
    time.sleep(2)

    # dictionary to store data from post request
    ballot_data = {}

    users = utils.load_csv(paths.USERS_PATH)
    for user in users:
        # login as user
        auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])

        ballot_post_resp = ballot_requests.post_ballot(user_session=admin_session,
                                                       election_id=election_id,
                                                       position_id=position_id,
                                                       student_id=user['wwuid'],
                                                       vote=user['username'])
        ballot_resp_data = json.loads(ballot_post_resp.text)
        ballot_data[ballot_resp_data['id']] = ballot_resp_data

    for ballot_id, ballot in ballot_data.items():
        spec_get_resp = ballot_requests.get_specified_ballot(admin_session, election_id, ballot_id)
        assert (spec_get_resp.status_code == 200)
        spec_get_resp_data = json.loads(spec_get_resp.text)
        utils.assert_is_equal_sub_dict(ballot, spec_get_resp_data)
        print(spec_get_resp_data)

