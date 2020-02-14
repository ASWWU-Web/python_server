# sheldon woodward
# jan 17, 2019

from datetime import datetime

import src.aswwu.alchemy_new.elections as elections_alchemy
import src.aswwu.alchemy_new.mask as mask_alchemy
import src.aswwu.exceptions as exceptions

datetime_format = '%Y-%m-%d %H:%M:%S.%f'


def validate_parameters(given_parameters, required_parameters):
    """
    Validate that the given parameters match the required parameters.
    :param given_parameters: The parameters passed to the request.
    :param required_parameters: The parameters that must be present in the request.
    :return: None
    """
    # check for missing parameters
    for parameter in required_parameters:
        if parameter not in given_parameters.keys():
            raise exceptions.BadRequest400Exception('missing parameters')

    # check for too many parameters
    if len(required_parameters) != len(list(given_parameters.keys())):
        raise exceptions.BadRequest400Exception('too many parameters')

    # check for bad election type
    if 'election_type' in given_parameters.keys() and given_parameters['election_type'] not in ('aswwu', 'senate'):
        raise exceptions.BadRequest400Exception('election_type is not aswwu or senate')


def validate_election(parameters, existing_election=None):
    """
    Validate an election's parameters based on constraints.
    :param parameters: The election's parameters.
    :param existing_election: An existing election to not compare against during validation.
    :return: None
    """
    # check if start and end are valid datetime strings
    try:
        datetime.strptime(parameters['start'], datetime_format)
        datetime.strptime(parameters['end'], datetime_format)
    except ValueError as e:
        raise exceptions.BadRequest400Exception(e.message)

    # checking that election doesn't start or end in the past
    now = datetime.now().strftime(datetime_format)
    if parameters['start'] < now or parameters['end'] < now:
        raise exceptions.Forbidden403Exception('election takes place during the past')

    # check that end time isn't less than start time
    print(parameters['start'])
    print(parameters['end'])
    if parameters['start'] > parameters['end']:
        raise exceptions.Forbidden403Exception('start time is after end time')

    # check that election doesn't overlap with current or upcoming elections
    if elections_alchemy.detect_election_overlap(parameters["start"], parameters["end"], existing_election):
        raise exceptions.Forbidden403Exception('election takes place during another election')

    # check that max_votes is at least one
    if int(parameters['max_votes']) < 1:
        raise exceptions.Forbidden403Exception('max_votes must be at least one')


def validate_position(parameters):
    """
    Validate a position's parameters based on constraints.
    :param parameters: The position's parameters.
    :return: None
    """
    # check active parameter's type
    if not isinstance(parameters['active'], bool):
        raise exceptions.BadRequest400Exception('parameter active has type bool')

    # check order parameter's type
    if not isinstance(parameters['order'], int):
        raise exceptions.BadRequest400Exception('parameter order has type integer')

    # check that order parameter is >= 0
    if parameters['order'] < 0:
        raise exceptions.Forbidden403Exception('parameter order must be greater than or equal to 0')


def validate_vote(parameters, existing_vote=None):
    """
    Validate a vote's parameters based on constraints.
    :param parameters: The vote's parameters.
    :param existing_vote: An existing vote being updated used to check for duplicate votes.
    :return: None
    """
    # check if election exists
    specified_election = elections_alchemy.query_election(election_id=parameters['election'])
    if specified_election == list():
        raise exceptions.NotFound404Exception('election with specified ID not found')

    # check if not current election
    current_election = elections_alchemy.query_current()
    if specified_election[0] != current_election:
        raise exceptions.Forbidden403Exception('this election is not available for voting')

    # check if position exists and is active
    specified_position = elections_alchemy.query_position(position_id=parameters['position'])
    if specified_position == list() or specified_position[0].active is False:
        raise exceptions.Forbidden403Exception('position with specified ID not found')

    # check if position is the right election type
    if specified_position[0].election_type != current_election.election_type:
        raise exceptions.Forbidden403Exception('you are voting for a position in a different election type')

    # check for valid candidate username
    if mask_alchemy.query_by_username(parameters['vote']) is None:
        raise exceptions.Forbidden403Exception('you cannot vote for this person')

    # check for duplicate votes
    if parameters['vote'] != getattr(existing_vote, 'vote', None) and \
            elections_alchemy.query_vote(election_id=specified_election[0].id,
                                         position_id=specified_position[0].id,
                                         vote=parameters['vote'],
                                         username=parameters['username']) != list():
        raise exceptions.Forbidden403Exception('you have already voted for this person')


def validate_ballot(parameters):
    """
    Validate a ballot's parameters based on constraints.
    :param parameters: The ballot's parameters.
    :return: None
    """
    # check if election exists
    specified_election = elections_alchemy.query_election(election_id=parameters['election'])
    if specified_election == list():
        raise exceptions.NotFound404Exception('election with specified ID not found')

    # check if position exists and is active
    specified_position = elections_alchemy.query_position(position_id=parameters['position'])
    if specified_position == list() or specified_position[0].active is False:
        raise exceptions.Forbidden403Exception('position with specified ID not found')

    # check if position is the right election type
    if specified_position[0].election_type != specified_election[0].election_type:
        raise exceptions.Forbidden403Exception('you are creating a vote for a position in a different election type')

    # check for valid candidate username
    if mask_alchemy.query_by_username(parameters['vote']) is None:
        raise exceptions.Forbidden403Exception('you cannot create a vote for this candidate')

    # check for duplicate votes
    if elections_alchemy.query_vote(election_id=specified_election[0].id,
                                    position_id=specified_position[0].id,
                                    vote=parameters['vote'],
                                    username=parameters['username']) != list():
        raise exceptions.Forbidden403Exception('this candidate has already been voted for by this user')


def validate_candidate(parameters):
    """
    Validate a candidate's parameters based on constraints.
    :param parameters: The candidate's parameters.
    :return: None
    """
    # check to make sure there is an election to push candidates to
    election = elections_alchemy.query_election(election_id=parameters['election'])
    if election == list():
        raise exceptions.NotFound404Exception('election with specified ID not found')
    election = election[0]

    # check to make sure election is either current or up and coming
    if election != elections_alchemy.query_current() and \
            election not in elections_alchemy.query_election(start_after=datetime.now()):
        raise exceptions.Forbidden403Exception('candidate not in current election')

    # check to makes sure position exists
    if not elections_alchemy.query_position(position_id=str(parameters["position"])):
        raise exceptions.NotFound404Exception('position with specified ID not found')

    # check to make sure election exists
    if not elections_alchemy.query_election(election_id=parameters['election']):
        raise exceptions.NotFound404Exception('election with specified ID not found')
