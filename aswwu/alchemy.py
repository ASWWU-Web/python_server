# alchemy.py

# import and set up the logging
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload

logger = logging.getLogger("aswwu")

# import the necessary models (all of them in this case)

# defines the databases URLs relative to "server.py"
engine = create_engine("sqlite:///../databases/people.db")
archive_engine = create_engine("sqlite:///../databases/archives.db")
election_engine = create_engine("sqlite:///../databases/senate_elections.db")
pages_engine = create_engine("sqlite:///../databases/pages.db")
jobs_engine = create_engine("sqlite:///../databases/jobs.db")

# create the model tables if they don't already exist
Base.metadata.create_all(engine)
ElectionBase.metadata.create_all(election_engine)
PagesBase.metadata.create_all(pages_engine)
JobsBase.metadata.create_all(jobs_engine)

# bind instances of the databases to corresponding variables
Base.metadata.bind = engine
dbs = sessionmaker(bind=engine)
s = dbs()
# same for archives
ArchiveBase.metadata.bind = archive_engine
archive_dbs = sessionmaker(bind=archive_engine)
archive_s = archive_dbs()
#same for elections
ElectionBase.metadata.bind = election_engine
election_dbs = sessionmaker(bind=election_engine)
election_s = election_dbs()
#same for pages
PagesBase.metadata.bind = election_engine
pages_dbs = sessionmaker(bind=pages_engine)
page_s = pages_dbs()

JobsBase.metadata.bind = election_engine
jobs_dbs = sessionmaker(bind=jobs_engine)
jobs_s = jobs_dbs()


# updates a model, or creates it if it doesn't exist
def addOrUpdate(thing):
    try:
        s.add(thing)
        s.commit()
        return thing
    except Exception as e:
        logger.info(e)
        s.rollback()


# finds all rows for a given model
def query_all(model):
    thing = None
    try:
        thing = s.query(model).all()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing


# finds all rows for a given model matching the given WWUID
def query_by_wwuid(model, wwuid):
    thing = None
    try:
        thing = s.query(model).filter_by(wwuid=str(wwuid)).all()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing


# finds all rows for a given model matching the given ID
def query_by_id(model, id):
    thing = None
    try:
        thing = s.query(model).filter_by(id=id).first()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing


# finds all rows for a given model matching the given field=value
def query_by_field(model, field, value):
    thing = None
    try:
        thing = s.query(model).filter(getattr(model, field).like(value)).all()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing


# finds a user with the given WWUID
def query_user(wwuid):
    thing = query_by_wwuid(User, str(wwuid))
    if thing:
        thing = thing[0]
    return thing


# permanently deletes a given model
def delete_thing(thing):
    try:
        s.delete(thing)
        s.commit()
    except Exception as e:
        logger.info(e)
        s.rollback()


def query_all_Election(model):
    thing = None
    try:
        thing = election_s.query(model).all()
    except Exception as e:
        logger.info(e)
        election_s.rollback()
    return thing


def addOrUpdateElection(thing):
    try:
        election_s.add(thing)
        election_s.commit()
        return thing
    except Exception as e:
        logger.info(e)
        election_s.rollback()


# finds all rows for a given model matching the given WWUID
def query_by_wwuid_Election(model, wwuid):
    thing = None
    try:
        thing = election_s.query(model).filter_by(wwuid=str(wwuid)).all()
    except Exception as e:
        logger.info(e)
        election_s.rollback()
    return thing


# updates a model, or creates it if it doesn't exist
def addOrUpdatePage(thing):
    try:
        page_s.add(thing)
        page_s.commit()
        return thing
    except Exception as e:
        logger.info(e)
        page_s.rollback()


def query_by_page_url(model, url):
    thing = None
    try:
        thing = page_s.query(model).options(joinedload('*')).filter_by(url=str(url)).all()
    except Exception as e:
        logger.info(e)
        page_s.rollback()
    return thing


def query_by_page_id(model, page_id):
    thing = None
    try:
        thing = page_s.query(model).options(joinedload('*')).filter_by(id=str(page_id)).all()
    except Exception as e:
        logger.info(e)
        page_s.rollback()
    return thing


def query_by_page_url(model, url):
    thing = None
    try:
        thing = page_s.query(model).options(joinedload('*')).filter_by(url=str(url)).all()
    except Exception as e:
        logger.info(e)
        page_s.rollback()
    return thing

# def query_page(page_id):
#     thing = None
#     try:
#         thing = query_by_page_id(User, str(page_id))
#         if thing:
#             thing = thing[0]
#     except Exception as e:
#         logger.info(e)
#         page_s.rollback()
#     return thing


# updates a model, or creates it if it doesn't exist
def addOrUpdateForm(thing):
    try:
        jobs_s.add(thing)
        jobs_s.commit()
        return thing
    except Exception as e:
        logger.info(e)
        jobs_s.rollback()

def query_by_job_name(model, name):
    thing = None
    try:
        thing = jobs_s.query(model).options(joinedload('*')).filter_by(job_name=str(name)).all()
    except Exception as e:
        logger.info(e)
        jobs_s.rollback()
    return thing

def query_all_Forms(model):
    thing = None
    try:
        thing = jobs_s.query(model).all()
    except Exception as e:
        logger.info(e)
        jobs_s.rollback()
    return thing

# permanently deletes a given model
def delete_thing_Forms(thing):
    try:
        jobs_s.delete(thing)
        jobs_s.commit()
    except Exception as e:
        logger.info(e)
        jobs_s.rollback()
