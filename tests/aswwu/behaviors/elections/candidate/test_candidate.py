import tests.aswwu.behaviors.elections.candidate.candidate_requests as candidate_requests
import tests.aswwu.behaviors.elections.candidate.candidate_subtests as candidate_subtests
import json
from tests.conftest import testing_server


def test_post_candidate(testing_server):
    candidate_subtests.create_candidates()


def test_get_candidate(testing_server):
    candidate_data, election_id = candidate_subtests.create_candidates()
    resp = candidate_requests.get_candidate(election_id)
    assert(resp.status_code == 200)
    resp_data = json.loads(resp.text)['candidates']
    for candidate in resp_data:
        assert (candidate['id'] in candidate_data)
        candidate_subtests.assert_candidate_data(candidate, candidate_data[candidate['id']])


def test_get_specified_candidate(testing_server):
    candidate_data, election_id = candidate_subtests.create_candidates()
    for candidate_id, candidate in candidate_data.items():
        resp = candidate_requests.get_specified_candidate(election_id, candidate_id)
        assert(resp.status_code == 200)
        resp_data = json.loads(resp.text)
        candidate_subtests.assert_candidate_data(resp_data, candidate)


def test_put_specified_candidate(testing_server):
    candidate_data, election_id = candidate_subtests.create_candidates()