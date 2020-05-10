import tests.aswwu.behaviors.elections.candidate.candidate_requests as candidate_requests
import tests.aswwu.behaviors.elections.candidate.candidate_subtests as candidate_subtests
import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import json
from tests.conftest import testing_server


def test_post_candidate(testing_server):
    session = election_subtests.create_elections_admin()
    candidate_subtests.create_candidates(session)


def test_get_candidate(testing_server):
    session = election_subtests.create_elections_admin()
    candidate_data, election_id = candidate_subtests.create_candidates(session)[0:2]
    resp = candidate_requests.get_candidate(election_id)
    assert(resp.status_code == 200)
    resp_data = json.loads(resp.text)['candidates']
    for candidate in resp_data:
        assert (candidate['id'] in candidate_data)
        candidate_subtests.assert_candidate_data(candidate, candidate_data[candidate['id']])


def test_get_specified_candidate(testing_server):
    session = election_subtests.create_elections_admin()
    candidate_data, election_id = candidate_subtests.create_candidates(session)[0:2]
    for candidate_id, candidate in candidate_data.items():
        resp = candidate_requests.get_specified_candidate(election_id, candidate_id)
        assert(resp.status_code == 200)
        resp_data = json.loads(resp.text)
        candidate_subtests.assert_candidate_data(resp_data, candidate)


def test_put_specified_candidate(testing_server):
    session = election_subtests.create_elections_admin()
    candidate_data, election_id, position_ids = candidate_subtests.create_candidates(session)

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
        candidate_subtests.assert_candidate_data(json.loads(resp.text), updated_candidate_data)
