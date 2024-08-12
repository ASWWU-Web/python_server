import settings

ELECTION_URL = settings.config['base_url'] + ':' + str(settings.config['port']) + '/' + 'elections/election'


def get_ballot(admin_session, election_id, position_id=None, vote=None):
    """
    Retrieve all manually entered votes in the specified election.
    GET (r"/elections/election/(.*)/ballot", elections.BallotHandler)
    :param admin_session: logged in election-admin session
    :param election_id: id of election to query
    :param position_id: optional, id of position to filter query by
    :param vote: optional, vote to filter query by
    :return: the request response body
    """
    url = ELECTION_URL + '/' + election_id + '/ballot'
    optional_parameters = {
        'position': position_id,
        'vote': vote
    }
    resp = admin_session.get(url, params=optional_parameters)
    return resp


def post_ballot(user_session, election_id, position_id, student_id, vote):
    """
    Create a manually entered vote for the specified election.
    POST (r"/elections/election/(.*)/ballot", elections.BallotHandler)
    :param user_session: logged-in user session
    :param election_id: id of election to post ballot to
    :param position_id: id of position for ballot
    :param student_id: id of user voting (wwuid)
    :param vote: username of person being voted for
    :return: the request response object
    """
    url = ELECTION_URL + '/' + election_id + '/ballot'
    post_data = {
      'election': election_id,
      'position': position_id,
      'student_id': student_id,
      'vote': vote
    }
    resp = user_session.post(url, json=post_data)
    return resp


def get_specified_ballot(admin_session, election_id, vote_id):
    """
    Retrieve a manually entered vote.
    GET (r"/elections/election/(.*)/ballot/(.*)", elections.SpecifiedBallotHandler)
    :param admin_session: logged in election-admin session
    :param election_id: id of election to get ballot from
    :param vote_id: id of vote to get
    :return: the request response object
    """
    url = ELECTION_URL + '/' + election_id + '/ballot/' + vote_id
    resp = admin_session.get(url)
    return resp


def delete_specified_ballot(admin_session, election_id, vote_id):
    """
    Destroy a manually entered vote.
    DELETE (r"/elections/election/(.*)/ballot/(.*)", elections.SpecifiedBallotHandler)
    :param admin_session: logged in election-admin session
    :param election_id: id of election to delete ballot from
    :param vote_id: id of vote to destroy
    :return: the request response object
    """
    url = ELECTION_URL + '/' + election_id + '/ballot/' + vote_id
    resp = admin_session.delete(url)
    return resp
