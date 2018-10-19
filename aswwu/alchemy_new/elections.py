# elections.py

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import aswwu.models.bases as base
import aswwu.models.elections as election_model

ElectionBase = base.ElectionBase

logger = logging.getLogger("aswwu")

# defines the databases URLs relative to "server.py"
election_engine = create_engine("sqlite:///../databases/senate_elections.db")
# create the model tables if they don't already exist
ElectionBase.metadata.create_all(election_engine)

# same for elections
ElectionBase.metadata.bind = election_engine
election_dbs = sessionmaker(bind=election_engine)
election_db = election_dbs()


def query_all_election(model):
    thing = None
    try:
        thing = election_db.query(model).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def add_or_update_election(thing):
    try:
        election_db.add(thing)
        election_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        election_db.rollback()


def query_district_election(district):
    thing = None
    try:
        thing = election_db.query(election_model.Candidate).filter_by(district=str(district)).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def query_candidate_election(username):
    thing = None
    try:
        thing = election_db.query(election_model.Candidate).filter_by(username=str(username)).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


# finds all rows for a given model matching the given WWUID
def query_vote_election(username):
    thing = None
    try:
        thing = election_db.query(election_model.Vote).filter_by(username=str(username)).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing

