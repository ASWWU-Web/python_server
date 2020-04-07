import json
import tests.aswwu.behaviors.elections.election.election_requests as election_requests
from tests.utils import load_csv
from tests.aswwu.data.paths import ELECTIONS_PATH

from datetime import datetime, timedelta


def send_get_election():
    resp = election_requests.get_election()
    assert (resp.status_code == 200)
    resp_text = json.loads(resp.text)
    elections_csv = load_csv(ELECTIONS_PATH)

    for i in range(len(resp_text['elections'])):
        assert (resp_text['elections'][i]['election_type'] == elections_csv[i]['election_type'])
        assert (resp_text['elections'][i]['name'] == elections_csv[i]['name'])
        assert (int(resp_text['elections'][i]['max_votes']) == int(elections_csv[i]['max_votes']))
        assert (resp_text['elections'][i]['start'] == elections_csv[i]['start'])
        assert (resp_text['elections'][i]['end'] == elections_csv[i]['end'])
        assert (resp_text['elections'][i]['show_results'] == elections_csv[i]['show_results'])


def _post_election(election):
    resp = election_requests.post_election(election['election_type'], election['name'], election['max_votes'],
                                           election['start'], election['end'], election['show_results'])
    resp_text = json.loads(resp.text)
    assert (resp.status_code == 201)
    assert (resp_text['election_type'] == election['election_type'])
    assert (resp_text['name'] == election['name'])
    assert (int(resp_text['max_votes']) == int(election['max_votes']))
    assert (resp_text['start'] == election['start'])
    assert (resp_text['end'] == election['end'])
    assert (resp_text['show_results'] == election['show_results'])
    return resp_text


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
    _post_election(new_election)


def send_get_current():
    resp = election_requests.get_current()
    resp_text = json.loads(resp.text)
    assert(resp.status_code == 200)
    assert(datetime.strptime(resp_text['end'], "%Y-%m-%d %H:%M:%S.%f") >= datetime.now())
