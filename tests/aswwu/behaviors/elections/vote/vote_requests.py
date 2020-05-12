import requests
from settings import keys, testing

VOTE_URL = testing['base_url'] + ':' + str(testing['port']) + '/' + 'elections/vote'


def post_vote(session, election=None, position=None, vote=None, obj_data=None):
    if obj_data is None:
        post_data = {
            'election': election,
            'position': position,
            'vote': vote,
        }
    else:
        post_data = obj_data
    resp = session.post(VOTE_URL, json=post_data)
    return resp


def get_vote(session, position_id, username):
    parameters = {
        'position': position_id,
        'vote': username
    }
    resp = session.get(VOTE_URL, params=parameters)
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