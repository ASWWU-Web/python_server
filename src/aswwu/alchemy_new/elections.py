# elections.py

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import src.aswwu.models.bases as base
import src.aswwu.models.elections as elections_model
from datetime import datetime
# from settings import database
from settings import environment

ElectionBase = base.ElectionBase

logger = logging.getLogger(environment["log_name"])

# defines the databases URLs relative to "server.py"
election_engine = create_engine("sqlite:///" + environment['databases_location'] + "/elections.db")
# create the model tables if they don't already exist
ElectionBase.metadata.create_all(election_engine)

# same for elections
ElectionBase.metadata.bind = election_engine
election_dbs = sessionmaker(bind=election_engine)
election_db = election_dbs()


def add_or_update(thing):
    """
    Add or update a model instance in the database.
    :param thing: The instance to update.
    :return: Returns the newly updated object.
    """
    try:
        election_db.add(thing)
        election_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        election_db.rollback()
        raise Exception(e)


def delete(thing):
    """
    Delete a model instance in the database.
    :param thing: The instance to delete.
    :return: None
    """
    try:
        election_db.delete(thing)
        election_db.commit()
    except Exception as e:
        logger.info(e)
        election_db.rollback()


def query_vote(vote_id=None, election_id=None, position_id=None, vote=None, username=None, manual_entry=None):
    """
    Queries the database for votes matching the specified parameters.
    :param vote_id: A specific vote ID to query.
    :param election_id: The election ID to filter by.
    :param position_id: The position ID to filter by.
    :param vote: The vote to filter by.
    :param username: The username to filter by.
    :param manual_entry: Either boolean or a string. If boolean, will query all records that do or do not have manual
    entries. If string, will find all matching manual entries.
    :return: Returns a list of all matching objects in the query.
    """
    thing = None
    try:
        thing = election_db.query(elections_model.Vote)
        if vote_id is not None:
            thing = thing.filter_by(id=str(vote_id))
        if election_id is not None:
            thing = thing.filter_by(election=str(election_id))
        if position_id is not None:
            thing = thing.filter_by(position=str(position_id))
        if vote is not None:
            thing = thing.filter_by(vote=str(vote))
        if username is not None:
            thing = thing.filter_by(username=str(username))
        if manual_entry is not None:
            if isinstance(manual_entry, bool) and manual_entry:
                thing = thing.filter(elections_model.Vote.manual_entry != None).\
                    order_by(elections_model.Vote.updated_at.desc())
            elif isinstance(manual_entry, bool) and not manual_entry:
                thing = thing.filter(elections_model.Vote.manual_entry == None).\
                    order_by(elections_model.Vote.updated_at.desc())
            elif isinstance(manual_entry, str):
                thing = thing.filter_by(manual_entry=str(manual_entry)).\
                    order_by(elections_model.Vote.updated_at.desc())
        thing = thing.all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def query_position(position_id=None, position=None, election_type=None, active=None):
    """
    Queries the database for positions matching the specified parameters.
    :param position_id: A specific position ID to query.
    :param position: The position to filter by.
    :param election_type: The election type to filter by.
    :param active: The active status to filter by.
    :return: Returns a list of all matched objects in the query.
    """
    thing = None
    try:
        thing = election_db.query(elections_model.Position)
        if position_id is not None:
            thing = thing.filter_by(id=str(position_id))
        if position is not None:
            thing = thing.filter_by(position=str(position))
        if election_type is not None:
            thing = thing.filter_by(election_type=str(election_type))
        if active == 'true' or active is True:
            thing = thing.filter_by(active=True)
        elif active == 'false' or active is False:
            thing = thing.filter_by(active=False)
        thing = thing.order_by(elections_model.Position.order).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def query_election(election_id=None, election_type=None, name=None, max_votes=None,
                   start_before=None, start_after=None, end_before=None, end_after=None):
    """
    Queries the database for elections matching the specified parameters.
    :param election_id: A specific election ID to query.
    :param election_type: The election type to filter by.
    :param name: The name to filter by.
    :param max_votes: The max_votes value to filter by.
    :param start_before: The maximum start date to filter by.
    :param start_after: The minimum start date to filter by.
    :param end_before: The maximum end date to filter by.
    :param end_after: The minimum end date to filter by.
    :return: Returns a list of all matched objects in the query.
    """
    thing = None
    try:
        thing = election_db.query(elections_model.Election)
        if election_id is not None:
            thing = thing.filter_by(id=election_id)
        if election_type is not None:
            thing = thing.filter_by(election_type=str(election_type))
        if name is not None:
            thing = thing.filter_by(name=str(name))
        if max_votes is not None:
            thing = thing.filter_by(max_votes=max_votes)
        if start_before is not None:
            thing = thing.filter(elections_model.Election.start <= start_before)
        if start_after is not None:
            thing = thing.filter(elections_model.Election.start >= start_after)
        if end_before is not None:
            thing = thing.filter(elections_model.Election.end <= end_before)
        if end_after is not None:
            thing = thing.filter(elections_model.Election.end >= end_before)
        thing = thing.all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def query_current():
    """
    Queries the database for an election that is currently taking place.
    :return: Returns the matched election object or None if not found.
    """
    thing = None
    try:
        thing = election_db.query(elections_model.Election) \
            .filter(elections_model.Election.end >= datetime.now()) \
            .filter(elections_model.Election.start <= datetime.now()) \
            .order_by(elections_model.Election.start.asc()) \
            .first()
    except Exception as i:
        logger.info(i)
        election_db.rollback()
    return thing


def query_current_or_upcoming():
    """
    Queries the database for an election that is current or upcoming election.
    :return: Returns the matched election object or None if not found.
    """
    thing = None
    try:
        thing = election_db.query(elections_model.Election) \
            .filter(elections_model.Election.end >= datetime.now()) \
            .order_by(elections_model.Election.start.asc()) \
            .first()

    except Exception as i:
        logger.info(i)
        election_db.rollback()
    return thing


def query_candidates(candidate_id=None, election_id=None, position_id=None, username=None, display_name=None):
    """
    Queries the database for candidates matching the specified parameters.
    :param candidate_id: A specific candidate ID to query.
    :param election_id: A specific election ID to query.
    :param position_id: A specific position ID to query.
    :param username: The username to filter by.
    :param display_name: The display name to filter by.
    :return: Returns a list of matched objects in the query.
    """
    thing = None
    try:
        thing = election_db.query(elections_model.Candidate)
        if candidate_id is not None:
            thing = thing.filter_by(id=str(candidate_id))
        if election_id is not None:
            thing = thing.filter_by(election=str(election_id))
        if position_id is not None:
            thing = thing.filter_by(position=str(position_id))
        if username is not None:
            thing = thing.filter_by(username=str(username))
        if display_name is not None:
            thing = thing.filter_by(display_name=str(display_name))
        thing = thing.all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def detect_election_overlap(start, end, existing_election=None):
    """
    Queries the database for an election that has overlapping times with the specified times.
    :param start: The start date to check for.
    :param end: The end date to check for.
    :param existing_election: The election that is being updated. Used to prevent detecting sel overlaps.
    :return: Returns True if an overlap occurs or False if an overlap does not occur.
    """
    try:
        # check overlapping start date
        thing = election_db.query(elections_model.Election) \
            .filter(elections_model.Election.start >= start) \
            .filter(elections_model.Election.start <= end) \
            .filter(elections_model.Election.id != getattr(existing_election, 'id', None))
        if len(thing.all()) > 0:
            return True

        # check overlapping end date
        thing = election_db.query(elections_model.Election) \
            .filter(elections_model.Election.end >= start) \
            .filter(elections_model.Election.end <= end) \
            .filter(elections_model.Election.id != getattr(existing_election, 'id', None))
        if len(thing.all()) > 0:
            return True

        # check outside containing dates
        thing = election_db.query(elections_model.Election) \
            .filter(elections_model.Election.start <= start) \
            .filter(elections_model.Election.end >= end) \
            .filter(elections_model.Election.id != getattr(existing_election, 'id', None))
        if len(thing.all()) > 0:
            return True

        # check inside containing dates
        thing = election_db.query(elections_model.Election) \
            .filter(elections_model.Election.start >= start) \
            .filter(elections_model.Election.end <= end) \
            .filter(elections_model.Election.id != getattr(existing_election, 'id', None))
        if len(thing.all()) > 0:
            return True
    except Exception as j:
        logger.info(j)
        election_db.rollback()
    return False


def count_votes(election_id, position_id):
    """
    Queries the database and tallies votes for every user in the specified election and position.
    :param election_id: The election to tally votes for.
    :param position_id: The position to tally votes for.
    :return: Returns a list of dictionaries each containing the candidate's username and number of votes.
    """
    totals = list()
    # iterate over all unique usernames as votes
    for vote_username in election_db.query(elections_model.Vote.vote) \
            .filter_by(election=str(election_id), position=str(position_id)) \
            .distinct():
        # count all votes for the username
        num_votes = election_db.query(elections_model.Vote) \
            .filter_by(election=str(election_id), position=str(position_id), vote=vote_username[0]) \
            .count()
        # add vote count object to the list
        count_dict = {
            'candidate': vote_username[0],
            'votes': num_votes
        }
        totals.append(count_dict)
    return totals
