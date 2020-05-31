import tests.aswwu.behaviors.elections.candidate.candidate_requests as candidate_requests
import tests.aswwu.behaviors.elections.candidate.candidate_utils as candidate_utils
import tests.aswwu.behaviors.elections.election.election_utils as election_utils
import json
from tests.conftest import testing_server


def test_post_candidate(testing_server):
    session = election_utils.create_elections_admin()[1]
    election_id, position_ids = candidate_utils.create_default_candidate_params(session)
    candidate_utils.create_candidates(session, election_id, position_ids)


def test_get_candidate(testing_server):
    session = election_utils.create_elections_admin()[1]
    election_id, position_ids = candidate_utils.create_default_candidate_params(session)
    candidate_data = candidate_utils.create_candidates(session, election_id, position_ids)

    resp = candidate_requests.get_candidate(election_id)
    assert(resp.status_code == 200)
    resp_data = json.loads(resp.text)['candidates']
    for candidate in resp_data:
        assert (candidate['id'] in candidate_data)
        candidate_utils.assert_candidate_data(candidate, candidate_data[candidate['id']])


def test_get_specified_candidate(testing_server):
    session = election_utils.create_elections_admin()[1]
    election_id, position_ids = candidate_utils.create_default_candidate_params(session)
    candidate_data = candidate_utils.create_candidates(session, election_id, position_ids)

    for candidate_id, candidate in candidate_data.items():
        resp = candidate_requests.get_specified_candidate(election_id, candidate_id)
        assert(resp.status_code == 200)
        resp_data = json.loads(resp.text)
        candidate_utils.assert_candidate_data(resp_data, candidate)


def test_put_specified_candidate(testing_server):
    session = election_utils.create_elections_admin()[1]
    election_id, position_ids = candidate_utils.create_default_candidate_params(session)
    candidate_data = candidate_utils.create_candidates(session, election_id, position_ids)

    for candidate_id, candidate in candidate_data.items():
        updated_candidate_data = {
            'id': candidate_id,
            'election': election_id,
            'position': position_ids[1] if candidate['position'] == position_ids[0] else position_ids[0],
            'username': candidate['username'] + '_updated',
            'display_name': candidate['display_name'] + '_updated'
        }
        resp = candidate_requests.put_specified_candidate(session, election_id, candidate_id, updated_candidate_data)
        assert (resp.status_code == 200)
        candidate_utils.assert_candidate_data(json.loads(resp.text), updated_candidate_data)


def test_delete_specified_candidate(testing_server):
    session = election_utils.create_elections_admin()[1]

    # create a bunch of candidates
    election_id, position_ids = candidate_utils.create_default_candidate_params(session)
    candidate_data = candidate_utils.create_candidates(session, election_id, position_ids)

    # delete candidate, check if deleted
    for candidate_id, candidate in candidate_data.items():
        resp = candidate_requests.delete_specified_candidate(session, election_id, candidate_id)
        assert (resp.status_code == 204)

        # verify candidate is deleted
        resp = candidate_requests.get_specified_candidate(election_id, candidate_id)
        assert (resp.status_code == 404)
