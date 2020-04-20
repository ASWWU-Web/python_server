import json
import tests.aswwu.behaviors.elections.election.election_requests as election_requests

def assert_election_data(resp_data, election):
    assert (resp_data['election_type'] == election['election_type'])
    assert (resp_data['name'] == election['name'])
    assert (int(resp_data['max_votes']) == int(election['max_votes']))
    assert (resp_data['start'] == election['start'])
    assert (resp_data['end'] == election['end'])
    assert (resp_data['show_results'] == election['show_results'])


def assert_post_election(session, election):
    resp = election_requests.post_election(session, election['election_type'], election['name'], election['max_votes'],
                                           election['start'], election['end'], election['show_results'])
    resp_data = json.loads(resp.text)
    assert (resp.status_code == 201)
    assert_election_data(resp_data, election)
    return json.loads(resp.text)