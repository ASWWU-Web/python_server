# alchemy.py

# import and set up the logging
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
import src.aswwu.models.bases as base
import src.aswwu.models.mask as mask_model
from src.aswwu.archive_models import ArchiveBase
from settings import DATABASE

Base = base.Base
ElectionBase = base.ElectionBase
PagesBase = base.PagesBase
JobsBase = base.JobsBase

logger = logging.getLogger("aswwu")

# import the necessary models (all of them in this case)

# defines the databases URLs relative to "server.py"
# ?check_same_thread=False should only be a temp fix
engine = create_engine(  # pylint: disable=C0103
    "sqlite://" + DATABASE['location'] + "/people.db?check_same_thread=False")
archive_engine = create_engine(  # pylint: disable=C0103
    "sqlite://" +
    DATABASE['location'] + "/archives.db?check_same_thread=False")
election_engine = create_engine(  # pylint: disable=C0103
    "sqlite://" +
    DATABASE['location'] + "/senate_elections.db?check_same_thread=False")
pages_engine = create_engine(  # pylint: disable=C0103
    "sqlite://" + DATABASE['location'] + "/pages.db?check_same_thread=False")
jobs_engine = create_engine(  # pylint: disable=C0103
    "sqlite://" + DATABASE['location'] + "/jobs.db?check_same_thread=False")

# create the model tables if they don't already exist
Base.metadata.create_all(engine)
ElectionBase.metadata.create_all(election_engine)
PagesBase.metadata.create_all(pages_engine)
JobsBase.metadata.create_all(jobs_engine)

# bind instances of the databases to corresponding variables
Base.metadata.bind = engine
dbs = sessionmaker(bind=engine)
people_db = dbs()
# same for archives
ArchiveBase.metadata.bind = archive_engine
archive_dbs = sessionmaker(bind=archive_engine)
archive_db = archive_dbs()
# same for elections
ElectionBase.metadata.bind = election_engine
election_dbs = sessionmaker(bind=election_engine)
election_db = election_dbs()
# same for pages
PagesBase.metadata.bind = election_engine
pages_dbs = sessionmaker(bind=pages_engine)
page_db = pages_dbs()

JobsBase.metadata.bind = election_engine
jobs_dbs = sessionmaker(bind=jobs_engine)
jobs_db = jobs_dbs()


# updates a model, or creates it if it doesn't exist
def add_or_update(thing):
    try:
        people_db.add(thing)
        people_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        people_db.rollback()


# finds all rows for a given model
def query_all(model):
    thing = None
    try:
        thing = people_db.query(model).all()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


# finds all rows for a given model matching the given WWUID
def query_by_wwuid(model, wwuid):
    thing = None
    try:
        thing = people_db.query(model).filter_by(wwuid=str(wwuid)).all()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


# finds all rows for a given model matching the given ID
def query_by_id(model, aid):
    thing = None
    try:
        thing = people_db.query(model).filter_by(id=aid).first()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


# finds all rows for a given model matching the given field=value
def query_by_field(model, field, value):
    thing = None
    try:
        thing = people_db.query(model).filter(getattr(model, field).like(value)).all()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


# finds a user with the given WWUID
def query_user(wwuid):
    thing = query_by_wwuid(mask_model.User, str(wwuid))
    if thing:
        thing = thing[0]
    return thing


# permanently deletes a given model
def delete_thing(thing):
    try:
        people_db.delete(thing)
        people_db.commit()
    except Exception as e:
        logger.info(e)
        people_db.rollback()


def query_all_election(model):
    return query_all_by_db(election_db, model)


def query_all_by_db(db, model):
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


# finds all rows for a given model matching the given WWUID
def query_by_wwuid_election(model, wwuid):
    thing = None
    try:
        thing = election_db.query(model).filter_by(wwuid=str(wwuid)).all()
    except Exception as e:
        logger.info(e)
        election_db.rollback()
    return thing


# updates a model, or creates it if it doesn't exist
def add_or_update_page(thing):
    try:
        page_db.add(thing)
        page_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        page_db.rollback()


def query_by_page_url(model, url):
    thing = None
    try:
        thing = page_db.query(model).options(joinedload('*')).filter_by(url=str(url)).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


def query_by_page_id(model, page_id):
    thing = None
    try:
        thing = page_db.query(model).options(joinedload('*')).filter_by(id=str(page_id)).all()
    except Exception as e:
        logger.info(e)
        page_db.rollback()
    return thing


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
