import tests.aswwu.behaviors.elections.election.election_subtests as election_subtests
import tests.aswwu.behaviors.elections.election.election_requests as election_requests
import json
from tests.conftest import testing_server


def test_get_current(testing_server):
    session = election_subtests.create_elections_admin()
    election_subtests.assert_post_dynamic_election(session)


def test_get_election(testing_server):
    session = election_subtests.create_elections_admin()
    election_data = election_subtests.create_elections(session)

    resp = election_requests.get_election()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['elections']

    for data in resp_data:
        election_subtests.assert_election_data(data, election_data[data['id']])


def test_post_election(testing_server):
    session = election_subtests.create_elections_admin()
    election_subtests.create_elections(session)


def test_get_specified_election(testing_server):
    session = election_subtests.create_elections_admin()
    election_data = election_subtests.create_elections(session)
    for key, election in election_data.items():
        resp = election_requests.get_specified_election(key)
        assert(resp.status_code == 200)
        election_subtests.assert_election_data(json.loads(resp.text), election)


def test_put_specified_election(testing_server):
    session = election_subtests.create_elections_admin()
    election_data = election_subtests.create_elections(session)
    for election_id, election in election_data.items():
        updated_election_data = {
            'election_type': 'aswwu' if election['election_type'] == 'senate' else 'senate',
            'name': election['name'] + '_updated',
            'max_votes': election['max_votes'] + 1,
            'start': election_subtests.add_hour_dt(election['start']),
            'end': election_subtests.add_hour_dt(election['end']),
            'show_results': election_subtests.add_hour_dt(election['show_results'])
        }
        resp = election_requests.put_specified_election(session, election_id, updated_election_data['election_type'], updated_election_data['name'],
                                                        updated_election_data['max_votes'], updated_election_data['start'], updated_election_data['end'],
                                                        updated_election_data['show_results'])
        assert (resp.status_code == 200)
        election_subtests.assert_election_data(json.loads(resp.text), updated_election_data)


def test_get_count(testing_server):
    pass
