import tests.aswwu.behaviors.elections.election.election_utils as election_utils
import tests.aswwu.behaviors.elections.vote.vote_utils as vote_utils
import tests.aswwu.behaviors.elections.election.election_requests as election_requests
import tests.aswwu.behaviors.elections.position.position_requests as position_requests
import json
import tests.utils as utils
from tests.conftest import testing_server


def test_get_current(testing_server):
    session = election_utils.create_elections_admin()
    election_utils.assert_post_dynamic_election(session)


def test_get_election(testing_server):
    session = election_utils.create_elections_admin()
    election_data = election_utils.create_elections(session)

    resp = election_requests.get_election()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['elections']

    for data in resp_data:
        election_utils.assert_election_data(data, election_data[data['id']])


def test_post_election(testing_server):
    session = election_utils.create_elections_admin()
    election_utils.create_elections(session)


def test_get_specified_election(testing_server):
    session = election_utils.create_elections_admin()
    election_data = election_utils.create_elections(session)
    for key, election in election_data.items():
        resp = election_requests.get_specified_election(key)
        assert(resp.status_code == 200)
        election_utils.assert_election_data(json.loads(resp.text), election)


def test_put_specified_election(testing_server):
    session = election_utils.create_elections_admin()
    election_data = election_utils.create_elections(session)
    for election_id, election in election_data.items():
        updated_election_data = {
            'election_type': 'aswwu' if election['election_type'] == 'senate' else 'senate',
            'name': election['name'] + '_updated',
            'max_votes': election['max_votes'] + 1,
            'start': election_utils.add_hour_dt(election['start']),
            'end': election_utils.add_hour_dt(election['end']),
            'show_results': election_utils.add_hour_dt(election['show_results'])
        }
        resp = election_requests.put_specified_election(session, election_id, updated_election_data['election_type'], updated_election_data['name'],
                                                        updated_election_data['max_votes'], updated_election_data['start'], updated_election_data['end'],
                                                        updated_election_data['show_results'])
        assert (resp.status_code == 200)
        election_utils.assert_election_data(json.loads(resp.text), updated_election_data)


def test_get_count(testing_server):
    """
    test tally all votes for election
    :param testing_server: pytest testing server
    """
    # create admin session
    session = election_utils.create_elections_admin()

    # create dynamic election
    election_id = election_utils.assert_post_dynamic_election(session)['id']

    # create generic position
    position_resp = position_requests.post_position(session, 'President', 'aswwu', 'True', '1')
    position_id = json.loads(position_resp.text)['id']

    # post votes in election
    expected_vote_data = vote_utils.create_votes(session, election_id, position_id)

    # manually count votes
    vote_counts = {}
    for username, expected_vote in expected_vote_data.items():
        if username not in vote_counts:
            vote_counts[username] = {}
            vote_counts[username]['candidate'] = username
            vote_counts[username]['votes'] = 0
        vote_counts[username]['votes'] += 1

    # count votes query
    resp = election_requests.get_count(session, election_id)

    # check resp data
    assert (resp.status_code == 200)
    resp_count_data = json.loads(resp.text)['positions'][0]

    for resp_vote in resp_count_data['votes']:
        utils.assert_is_equal_sub_dict(vote_counts[resp_vote['candidate']], resp_vote)

