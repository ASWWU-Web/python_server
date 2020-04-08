import json
import tests.aswwu.behaviors.elections.election.election_requests as election_requests
from tests.utils import load_csv
from tests.aswwu.data.paths import ELECTIONS_PATH

from datetime import datetime, timedelta


def send_get_election(elections):
    """elections is a dictionary with the id as the key and the value the rest of the election data"""
    resp = election_requests.get_election()
    assert (resp.status_code == 200)
    resp_data = json.loads(resp.text)['elections']

    for data in resp_data:
        _verify_election_data(data, elections[data['id']])


def send_get_specified_election(elections):
    for key, election in elections.items():
        resp = election_requests.get_specified_election(key)
        assert(resp.status_code == 200)
        resp_data = json.loads(resp.text)
        _verify_election_data(resp_data, election)


def _verify_election_data(resp_data, election_data):
    assert (resp_data['election_type'] == election_data['election_type'])
    assert (resp_data['name'] == election_data['name'])
    assert (int(resp_data['max_votes']) == int(election_data['max_votes']))
    assert (resp_data['start'] == election_data['start'])
    assert (resp_data['end'] == election_data['end'])
    assert (resp_data['show_results'] == election_data['show_results'])


def _post_election(election):
    resp = election_requests.post_election(election['election_type'], election['name'], election['max_votes'],
                                           election['start'], election['end'], election['show_results'])
    resp_data = json.loads(resp.text)
    assert (resp.status_code == 201)
    _verify_election_data(resp_data, election)
    return resp_data


def send_post_election():
    elections_data = {}
    elections = load_csv(ELECTIONS_PATH)
    for election in elections:
        data = _post_election(election)
        elections_data[data['id']] = data
    return elections_data


def send_post_dynamic_election():
    """For use with testing elections/current"""
    new_election = {
        'election_type': 'aswwu',
        'name': 'General Election Test',
        'max_votes': 2,
        'start': datetime.strftime(datetime.now() + timedelta(hours=1), '%Y-%m-%d %H:%M:%S.%f'),
        'end': datetime.strftime(datetime.now() + timedelta(days=1), '%Y-%m-%d %H:%M:%S.%f'),
        'show_results': datetime.strftime(datetime.now() + timedelta(days=1), '%Y-%m-%d %H:%M:%S.%f'),
    }
    return _post_election(new_election)


def send_get_current(election_data):
    resp = election_requests.get_current()
    resp_data = json.loads(resp.text)
    assert(resp.status_code == 200)
    assert(datetime.strptime(resp_data['end'], "%Y-%m-%d %H:%M:%S.%f") >= datetime.now())
    _verify_election_data(resp_data, election_data)
