# jobs.py

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload

import src.aswwu.models.bases as base
from settings import config

JobsBase = base.JobsBase

logger = logging.getLogger(config.logging.get('log_name'))

jobs_engine = create_engine("sqlite:///" + config.database.get('databases') + "/jobs.db")

JobsBase.metadata.create_all(jobs_engine)

# somone hooked this up to the elections engine once upon a time, never forget
JobsBase.metadata.bind = jobs_engine
jobs_dbs = sessionmaker(bind=jobs_engine)
jobs_db = jobs_dbs()


# updates a model, or creates it if it doesn't exist
def add_or_update_form(thing):
    try:
        jobs_db.add(thing)
        jobs_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        jobs_db.rollback()


def query_by_job_name(model, name):
    thing = None
    try:
        thing = jobs_db.query(model).options(joinedload('*')).filter_by(job_name=str(name)).all()
    except Exception as e:
        logger.info(e)
        jobs_db.rollback()
    return thing


def query_all_forms(model):
    thing = None
    try:
        thing = jobs_db.query(model).all()
    except Exception as e:
        logger.info(e)
        jobs_db.rollback()
    return thing


# permanently deletes a given model
def delete_thing_forms(thing):
    try:
        jobs_db.delete(thing)
        jobs_db.commit()
    except Exception as e:
        logger.info(e)
        jobs_db.rollback()
