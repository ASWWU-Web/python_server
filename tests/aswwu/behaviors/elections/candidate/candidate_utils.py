import tests.aswwu.behaviors.elections.election.election_utils as election_utils
import tests.aswwu.behaviors.elections.candidate.candidate_requests as candidate_requests
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import tests.aswwu.behaviors.elections.position.position_data as position_data
import tests.aswwu.behaviors.auth.auth_requests as auth_requests
from tests.aswwu.data.users import USERS
import json


def create_candidates(session,  election_id, position_ids):
    """
    creates a number of candidates for the given election
    :param session: an admin session used to create candidates
    :param position_ids: ids of positions to create candidates with
    :param election_id: a pre-existing election id
    :return: candidate data dictionary
    """
    candidate_data = {}
    num_positions = len(position_ids)

    for count, user in enumerate(USERS):
        response = auth_requests.post_verify(user['wwuid'], user['full_name'], user['email'])
        response_txt = json.loads(response.text)['user']
        response_txt['email'] = user['email']
        resp = candidate_requests.post_candidate(session,
                                                 election_id,
                                                 position_ids[count % num_positions],
                                                 user['username'],
                                                 user['full_name'])
        resp_data = json.loads(resp.text)
        candidate = {'position': position_ids[count % num_positions],
                     'username': user['username'],
                     'display_name': user['full_name']}
        assert (resp.status_code == 201)
        assert_candidate_data(resp_data, candidate)
        candidate_data[resp_data['id']] = resp_data
    return candidate_data


def assert_candidate_data(resp, candidate):
    assert(resp['position'] == candidate['position'])
    assert(resp['username'] == candidate['username'])
    assert(resp['display_name'] == candidate['display_name'])


def create_default_candidate_params(session):
    """
    creates a generic election and generic positions
    :param session: an admin session used to create candidates
    :return election_id: generic election id
    :return position_ids: generic position ids
    """
    election_id = election_utils.assert_post_dynamic_election(session)['id']
    position_resp_aswwu = position_requests.post_position(session,
                                                          position=position_data.ASWWU_DATA['position'],
                                                          election_type=position_data.ASWWU_DATA['election_type'],
                                                          active=position_data.ASWWU_DATA['active'],
                                                          order=position_data.ASWWU_DATA['order'])
    position_resp_senate = position_requests.post_position(session,
                                                           position=position_data.SENATOR_DATA['position'],
                                                           election_type=position_data.SENATOR_DATA['election_type'],
                                                           active=position_data.SENATOR_DATA['active'],
                                                           order=position_data.SENATOR_DATA['order'])
    position_ids = [json.loads(position_resp_aswwu.text)['id'], json.loads(position_resp_senate.text)['id']]
    return election_id, position_ids
