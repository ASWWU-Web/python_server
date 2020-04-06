import json
import tests.aswwu.behaviors.elections.elections_requests as elections_requests
from tests.utils import load_csv
from tests.aswwu.data.paths import ELECTIONS_PATH, POSITIONS_PATH

from datetime import datetime, timedelta


def send_get_election():
    resp = elections_requests.get_election()
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
    resp = elections_requests.post_election(election['election_type'], election['name'], election['max_votes'],
                                            election['start'], election['end'], election['show_results'])
    resp_text = json.loads(resp.text)
    assert (resp.status_code == 201)
    assert (resp_text['election_type'] == election['election_type'])
    assert (resp_text['name'] == election['name'])
    assert (int(resp_text['max_votes']) == int(election['max_votes']))
    assert (resp_text['start'] == election['start'])
    assert (resp_text['end'] == election['end'])
    assert (resp_text['show_results'] == election['show_results'])


def send_post_election():
    elections = load_csv(ELECTIONS_PATH)
    for election in elections:
        _post_election(election)


def send_post_dynamic_election():
    """For use with testing elections/current"""
    new_election = {
        'election_type': 'aswwu',
        'name': 'General Election Test',
        'max_votes': 2,
        'start': datetime.now(),
        'end': datetime.now() + timedelta(days=1),
        'show_results': datetime.now() + timedelta(days=1),
    }
    _post_election(new_election)


def send_get_current():
    resp = elections_requests.get_current()
    resp_text = json.loads(resp.text)
    assert(resp.status_code == 200)
    assert(datetime.strptime(resp_text['end'], "%Y-%m-%d %H:%M:%S.%f") >= datetime.now())


def send_get_position():
    resp = elections_requests.get_position()
    resp_text = json.loads(resp.text)
    assert(resp.status_code == 200)


def send_post_position():
    positions = load_csv(POSITIONS_PATH)
    for position in positions:
        resp = elections_requests.post_position(position['position'], position['election_type'], position['active'],
                                                position['order'])
        resp_text = json.loads(resp.text)
        assert (resp.status_code == 201)
        assert(resp_text['position'] == position['position'])
        assert(resp_text['election_type'] == position['election_type'])
        assert(str(resp_text['active']) == position['active'])
        assert(str(resp_text['order']) == position['order'])

