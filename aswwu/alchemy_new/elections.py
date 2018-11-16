# elections.py

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import aswwu.models.bases as base
import aswwu.models.elections as election_model
from datetime import datetime

ElectionBase = base.ElectionBase

logger = logging.getLogger("aswwu")

# defines the databases URLs relative to "server.py"
election_engine = create_engine("sqlite:///../databases/elections.db")
# create the model tables if they don't already exist
ElectionBase.metadata.create_all(election_engine)

# same for elections
ElectionBase.metadata.bind = election_engine
election_dbs = sessionmaker(bind=election_engine)
election_db = election_dbs()


def add_or_update(thing):
    try:
        election_db.add(thing)
        election_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        election_db.rollback()
        raise Exception(e)


def query_vote(username):
    thing = None
    try:
        thing = election_db.query(election_model.Vote).filter_by(username=str(username)).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def query_election(election_id=None, election_type=None, start=None, end=None):
    thing = None
    try:
        thing = election_db.query(election_model.Election)
        if election_type is not None:
            thing = thing.filter_by(election_type=str(election_type))
        if start is not None:
            thing = thing.filter(election_model.Election.start >= start)
        if end is not None:
            thing = thing.filter(election_model.Election.end <= end)
        if election_id is not None:
            thing = thing.filter_by(id=election_id)
        thing = thing.all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def query_current():
    thing = None
    try:
        thing = election_db.query(election_model.Election) \
            .filter(election_model.Election.end >= datetime.now()) \
            .order_by(election_model.Election.start.asc()) \
            .first()

    except Exception as i:
        logger.info(i)
        election_db.rollback()
    return thing


def detect_election_overlap(start, end):
    try:
        thing = election_db.query(election_model.Election)
        thing = thing.filter(election_model.Election.start >= start)
        thing = thing.filter(election_model.Election.start <= end)
        if len(thing.all()) > 0:
            return True

        thing = election_db.query(election_model.Election)
        thing = thing.filter(election_model.Election.end >= start)
        thing = thing.filter(election_model.Election.end <= end)
        if len(thing.all()) > 0:
            return True

        thing = election_db.query(election_model.Election)
        thing = thing.filter(election_model.Election.start <= start)
        thing = thing.filter(election_model.Election.end >= end)
        if len(thing.all()) > 0:
            return True

        thing = election_db.query(election_model.Election)
        thing = thing.filter(election_model.Election.start >= start)
        thing = thing.filter(election_model.Election.end <= end)
        if len(thing.all()) > 0:
            return True

    except Exception as j:
        logger.info(j)
        election_db.rollback()
    return False


def query_candidates(election_id=None, candidate_id=None, position=None, username=None, display_name=None):
    thing = None
    try:
        thing = election_db.query(election_model.Candidate)
        if candidate_id is not None:
            thing = thing.filter_by(id=str(candidate_id))
        if election_id is not None:
            thing = thing.filter_by(election=str(election_id))
        if position is not None:
            thing = thing.filter_by(position=str(position))
        if username is not None:
            thing = thing.filter_by(username=str(username))
        if display_name is not None:
            thing = thing.filter_by(display_name=str(display_name))
        thing = thing.all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing
