# jobs.py

import logging

from sqlalchemy.orm import sessionmaker, joinedload

from aswwu.alchemy_new import connection
import aswwu.models.bases as base

logger = logging.getLogger("aswwu")

JobsBase = base.JobsBase

# bind instances of the databases to corresponding variables
JobsBase.metadata.bind = connection
jobs_dbs = sessionmaker(bind=connection)
jobs_db = jobs_dbs()

# create the model tables if they don't already exist
JobsBase.metadata.create_all()


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
