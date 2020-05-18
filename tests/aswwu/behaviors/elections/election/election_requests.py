import settings
import requests

ELECTION_URL = settings.environment['base_url'] + ':' + str(settings.environment['port']) + '/' + 'elections/election'
CURRENT_URL = settings.environment['base_url'] + ':' + str(settings.environment['port']) + '/' + 'elections/current'

# (r"/elections/election/(.*)/ballot", elections.BallotHandler)
# get, post

# (r"/elections/election/(.*)/ballot/(.*)", elections.SpecifiedBallotHandler)
# get, delete


def get_current():
    """elections/current"""
    resp = requests.get(CURRENT_URL)
    return resp


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


def post_election(session, election_type, name, max_votes, start, end, show_results):
    """elections/election"""
    post_data = {
        'election_type': election_type,
        'name': name,
        'max_votes': max_votes,
        'start': start,
        'end': end,
        'show_results': show_results,
    }
    resp = session.post(ELECTION_URL, json=post_data)
    return resp


def get_specified_election(election_id):
    """elections/election/{election_id}"""
    url = ELECTION_URL + '/' + election_id
    resp = requests.get(url)
    return resp


def put_specified_election(session, election_id, election_type, name, max_votes, start, end, show_results):
    """elections/election/{election_id}"""
    post_data = {
        'id': election_id,
        'election_type': election_type,
        'name': name,
        'max_votes': max_votes,
        'start': start,
        'end': end,
        'show_results': show_results,
    }
    url = ELECTION_URL + '/' + election_id
    resp = session.put(url, json=post_data)
    return resp


def get_count(session, election_id):
    """
    (r"/elections/election/(.*)/count", elections.VoteCountHandler)
    :param session: admin session to query votes
    :param election_id: id of election to get votes from
    :return: the request response object
    """
    url = ELECTION_URL + '/' + election_id + '/count'
    resp = session.get(url)
    return resp
