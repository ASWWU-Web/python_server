import requests
from settings import keys, testing

VOTE_URL = testing['base_url'] + ':' + str(testing['port']) + '/' + 'elections/vote'


def post_vote(session, election, position, vote):
    post_data = {
        'election': election,
        'position': position,
        'vote': vote,
    }
    resp = session.post(VOTE_URL, json=post_data)
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

# (r"/elections/election/(.*)/count", elections.VoteCountHandler)
# get
# Should this go under election?