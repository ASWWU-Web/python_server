import json
import tests.aswwu.behaviors.elections.elections_requests as elections_requests
from tests.utils import load_csv
from tests.aswwu.data.paths import ELECTIONS_PATH


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


def send_post_election():
    elections = load_csv(ELECTIONS_PATH)
    for election in elections:
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


