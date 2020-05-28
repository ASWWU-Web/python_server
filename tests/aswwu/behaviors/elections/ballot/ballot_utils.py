import tests.aswwu.behaviors.elections.ballot.ballot_requests as ballot_requests
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
import tests.aswwu.data.paths as paths
import tests.utils as utils
import json


def assert_create_ballots(admin_session, admin_user_data, election, positions):
    """
    Creates ballots
    :param admin_session: session with election-admin privileges
    :param admin_user_data: user data for logged-in user
    :param election: election object to create ballots for (must be open)
    :param positions: list of position objects
    :return: ballot dictionary mapping id to ballot data
    """
    # only add position ids in election
    position_ids = []
    for i, position in enumerate(positions):
        if position['election_type'] == election['election_type']:
            position_ids.append(position['id'])

    # election id
    election_id = election['id']

    ballot_data = {}
    users = utils.load_csv(paths.USERS_PATH)
    for i, user in enumerate(users):
        # cycle through position ids
        position_id = position_ids[i % len(position_ids)]

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
        ballot_data[ballot_resp_data['id']] = ballot_resp_data

    return ballot_data
