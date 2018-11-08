# elections.py

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload

import aswwu.models.bases as base
import aswwu.models.elections as elections_model

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


def query_vote(username):
    thing = None
    try:
        thing = election_db.query(elections_model.Vote).filter_by(username=str(username)).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


def query_position(id=None, position=None, election_type=None, active=None):
    thing = None
    try:
        thing = election_db.query(elections_model.Position)
        if id is not None:
            thing = thing.filter_by(id=str(id))
        if position is not None:
            thing = thing.filter_by(position=str(position))
        if election_type is not None:
            thing = thing.filter_by(election_type=str(election_type))
        if active == 'true':
            thing = thing.filter_by(active=True)
        elif active == 'false':
            thing = thing.filter_by(active=False)
        thing = thing.all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()

    return thing
