import requests
from settings import keys, testing

VOTE_URL = testing['base_url'] + ':' + testing['port'] + '/' + 'elections/vote'
ELECTION_URL = testing['base_url'] + ':' + testing['port'] + '/' + 'elections/election'
CURRENT_URL = testing['base_url'] + ':' + testing['port'] + '/' + 'elections/current'
POSITION_URL = testing['base_url'] + ':' + testing['port'] + '/' + 'elections/position'

# (r"/elections/vote", elections.VoteHandler)
def post_vote(election, position, vote):
    post_data = {
        'election': election,
        'position': position,
        'vote': vote,
    }
    resp = requests.post(VOTE_URL, post_data)
    return resp


def get_vote():
    resp = requests.get(VOTE_URL)
    return resp

# (r"/elections/vote/(.*)", elections.SpecificVoteHandler)
# get, put, delete
# def get_specific_vote():
#
# def put_specific_vote():
#
# def delete_specific_vote():

# (r"/elections/election/(.*)/ballot", elections.BallotHandler)
# get, post


# (r"/elections/election/(.*)/ballot/(.*)", elections.SpecifiedBallotHandler)
# get, delete

# (r"/elections/election/(.*)/candidate", elections.CandidateHandler)
# get, post

# (r"/elections/election/(.*)/candidate/(.*)", elections.SpecifiedCandidateHandler)
# get, put, delete

# (r"/elections/position", elections.PositionHandler)
# get, post
def get_position():
    pass


def post_position(position, election_type, active, order):
    post_data = {
      'position': position,
      'election_type': election_type,
      'active': active == 'True',
      'order': int(order)
    }
    resp = requests.post(POSITION_URL, json=post_data)
    return resp


# (r"/elections/position/(.*)", elections.SpecifiedPositionHandler)
# get, put

# (r"/elections/election", elections.ElectionHandler)
# get, post
def get_election():
    """elections/election"""
    resp = requests.get(ELECTION_URL)
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


# (r"/elections/election/(.*)/count", elections.VoteCountHandler)
# get


def get_current():
    """elections/current"""
    resp = requests.get(CURRENT_URL)
    return resp
