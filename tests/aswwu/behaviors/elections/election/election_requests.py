import requests
from settings import keys, testing

ELECTION_URL = testing['base_url'] + ':' + testing['port'] + '/' + 'elections/election'
CURRENT_URL = testing['base_url'] + ':' + testing['port'] + '/' + 'elections/current'

# (r"/elections/election/(.*)/ballot", elections.BallotHandler)
# get, post

# (r"/elections/election/(.*)/ballot/(.*)", elections.SpecifiedBallotHandler)
# get, delete


def get_election(election_type=None, name=None, max_votes=None, start_before=None, start_after=None, end_before=None,
                 end_after=None):
    """elections/election"""
    optional_parameters = {
        'election_type': election_type,
        'name': name,
        'max_votes': max_votes,
        'start_before': start_before,
        'start_after': start_after,
        'end_before': end_before,
        'end_after': end_after
    }
    resp = requests.get(ELECTION_URL, params=optional_parameters)
    return resp


def get_specified_election(election_id):
    """elections/election/{election_id}"""
    url = ELECTION_URL + '/' + election_id
    resp = requests.get(url)
    return resp


def post_election(election_type, name, max_votes, start, end, show_results):
    """elections/election"""
    post_data = {
        'election_type': election_type,
        'name': name,
        'max_votes': max_votes,
        'start': start,
        'end': end,
        'show_results': show_results,
    }
    resp = requests.post(ELECTION_URL, json=post_data)
    return resp


def get_current():
    """elections/current"""
    resp = requests.get(CURRENT_URL)
    return resp
