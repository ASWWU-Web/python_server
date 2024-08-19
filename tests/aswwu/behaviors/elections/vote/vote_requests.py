import settings

VOTE_URL = settings.config.server.get('base_url') + ':' + str(settings.config.server.get('port')) + '/' + 'elections/vote'

def post_vote(session, election, position, vote):
    post_data = {
        'election': election,
        'position': position,
        'vote': vote,
    }
    resp = session.post(VOTE_URL, json=post_data)
    return resp


def get_vote(session, position_id, username):
    parameters = {
        'position': position_id,
        'vote': username
    }
    resp = session.get(VOTE_URL, params=parameters)
    return resp


def get_specified_vote(session, vote_id):
    """
    Retrieve a vote.
    GET (r"/elections/vote/(.*)", elections.SpecificVoteHandler)
    :param session: user session
    :param vote_id: vote id
    :return resp: the request response object
    """
    url = VOTE_URL + '/' + vote_id
    resp = session.get(url)
    return resp


def put_specified_vote(user_session, vote_id, election_id, position_id, vote, user_username):
    """
    Update a vote. Only works if the election is still open.
    PUT (r"/elections/vote/(.*)", elections.SpecificVoteHandler)
    :param user_session: logged in user session
    :param vote_id: id of vote to update
    :param election_id: id of election
    :param position_id: id of position
    :param vote: username of person voting for
    :param user_username: username of user that is voting
    :return resp: the request response object
    """
    post_data = {
        'id': vote_id,
        'election': election_id,
        'position': position_id,
        'vote': vote,
        'username': user_username
    }
    url = VOTE_URL + '/' + vote_id
    resp = user_session.put(url, json=post_data)
    return resp


def delete_specified_vote(user_session, vote_id):
    """
    Destroy a vote. Only works if the election is still open.
    DELETE (r"/elections/vote/(.*)", elections.SpecificVoteHandler)
    :param user_session: user session
    :param vote_id: id of vote to destroy
    :return: the request response object
    """
    url = VOTE_URL + '/' + vote_id
    resp = user_session.delete(url)
    return resp
