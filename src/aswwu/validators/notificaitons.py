# Michael Stacy
# May 11 2020

from datetime import datetime

import src.aswwu.alchemy_new.notifications as elections_alchemy
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


#def validate_election(parameters, existing_election=None):
#    """
#    Validate an election's parameters based on constraints.
#    :param parameters: The election's parameters.
#    :param existing_election: An existing election to not compare against during validation.
#    :return: None
#    """
#    # check if start and end are valid datetime strings
#    try:
#        datetime.strptime(parameters['start'], datetime_format)
#        datetime.strptime(parameters['end'], datetime_format)
#    except ValueError as e:
#        raise exceptions.BadRequest400Exception(e.message)
#
#    # checking that election doesn't start or end in the past
#    now = datetime.now().strftime(datetime_format)
#    if parameters['start'] < now or parameters['end'] < now:
#        raise exceptions.Forbidden403Exception('election takes place during the past')
#
#    # check that end time isn't less than start time
#    print(parameters['start'])
#    print(parameters['end'])
#    if parameters['start'] > parameters['end']:
#        raise exceptions.Forbidden403Exception('start time is after end time')
#
#    # check that election doesn't overlap with current or upcoming elections
#    if elections_alchemy.detect_election_overlap(parameters["start"], parameters["end"], existing_election):
#        raise exceptions.Forbidden403Exception('election takes place during another election')
#
#    # check that max_votes is at least one
#    if int(parameters['max_votes']) < 1:
#        raise exceptions.Forbidden403Exception('max_votes must be at least one')
