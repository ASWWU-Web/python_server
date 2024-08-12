import settings
import requests

ELECTION_URL = settings.config['base_url'] + ':' + str(settings.config['port']) + '/' + 'elections/election'


def post_candidate(session, election_id, position, username, display_name):
    """elections/election"""
    post_data = {
        'position': position,
        'username': username,
        'display_name': display_name
    }
    url = ELECTION_URL + '/' + election_id + '/candidate'
    resp = session.post(url, json=post_data)
    return resp


def get_candidate(election_id, position=None, username=None, display_name=None):
    optional_parameters = {
        'position': position,
        'username': username,
        'display_name': display_name
    }
    url = ELECTION_URL + '/' + election_id + '/candidate'
    resp = requests.get(url, params=optional_parameters)
    return resp


def get_specified_candidate(election_id, candidate_id):
    url = ELECTION_URL + '/' + election_id + '/candidate/' + candidate_id
    resp = requests.get(url)
    return resp


def put_specified_candidate(session, election_id, candidate_id, candidate_data):
    url = ELECTION_URL + '/' + election_id + '/candidate/' + candidate_id
    resp = session.put(url, json=candidate_data)
    return resp


def delete_specified_candidate(session, election_id, candidate_id):
    """
    Destroy a candidate. Only works if the election is still open.
    DELETE (r"/elections/election/(.*)/candidate/(.*)", elections.SpecifiedCandidateHandler)
    :param session: election-admin session
    :param election_id: id of election to delete candidate from
    :param candidate_id: id of candidate to destroy
    :return: the request response object
    """
    url = ELECTION_URL + '/' + election_id + '/candidate/' + candidate_id
    resp = session.delete(url)
    return resp
