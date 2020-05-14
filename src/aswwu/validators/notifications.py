# Michael Stacy
# May 11 2020

from datetime import datetime

import src.aswwu.exceptions as exceptions

datetime_format = '%Y-%m-%d %H:%M:%S.%f'
max_notification_length = 255


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


def validate_notification(parameters):
    """
    Validate an notification's parameters based on time constraints.
    :param parameters: The notification's parameters.
    :param existing_election: An existing notification to not compare against during validation.
    :return: None
    """
    # check if start and end are valid datetime strings
    try:
        datetime.strptime(parameters['start_time'], datetime_format)
        datetime.strptime(parameters['end_time'], datetime_format)
    except ValueError as e:
        raise exceptions.BadRequest400Exception(e.message)

    # checking that election doesn't start or end in the past
    now = datetime.now().strftime(datetime_format)
    if parameters['start_time'] < now or parameters['end_time'] < now:
        raise exceptions.Forbidden403Exception('notification takes place during the past')

    # check that end time isn't less than start time
    print(parameters['start_time'])
    print(parameters['end_time'])
    if parameters['start_time'] > parameters['end_time']:
        raise exceptions.Forbidden403Exception('start time is after end time')

    #check that the length isnt too long
    length = len(parameters['notification_text'])
    if length > max_notification_length:
        raise exceptions.Forbidden403Exception('notification text is too long')
