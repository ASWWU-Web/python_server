from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import logging
logger = logging.getLogger("aswwu")

ArchiveBase = declarative_base()
OldBase = declarative_base()

from alchemy.models import *
from alchemy.archive_models import *
from alchemy.old_models import *

engine = create_engine("sqlite:///../databases/people.db")
archive_engine = create_engine("sqlite:///../databases/archives.db")

Base.metadata.create_all(engine)


Base.metadata.bind = engine
dbs = sessionmaker(bind=engine)
s = dbs()

ArchiveBase.metadata.bind = archive_engine
archive_dbs = sessionmaker(bind=archive_engine)
archive_s = archive_dbs()

def addOrUpdate(thing):
    try:
        s.add(thing)
        s.commit()
        return thing
    except Exception as e:
        logger.info(e)
        s.rollback()

def query_all(model):
    thing = None
    try:
        thing = s.query(model).all()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing

def query_by_wwuid(model, wwuid):
    thing = None
    try:
        thing = s.query(model).filter_by(wwuid=wwuid).all()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing

def query_by_id(model, id):
    thing = None
    try:
        thing = s.query(model).filter_by(id=id).first()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing

def query_by_field(model, field, value):
    thing = None
    try:
        thing = s.query(model).filter(getattr(model, field).like(value)).all()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing

def query_user(wwuid):
    thing = query_by_wwuid(User, wwuid)
    if thing:
        thing = thing[0]
    return thing

def delete_thing(thing):
    try:
        s.delete(thing)
        s.commit()
    except Exception as e:
        logger.info(e)
        s.rollback()




old_engine = create_engine("sqlite:///../databases/people_old.db")
OldBase.metadata.bind = old_engine
old_dbs = sessionmaker(bind=old_engine)
old_s = old_dbs()
def query_old_all(table):
    thing = None
    if table == 'users':
        model = OldUser
    elif table == 'profiles':
        model = OldProfile
    elif table == 'volunteers':
        model = OldVolunteer
    try:
        thing = old_s.query(model).all()
    except Exception as e:
        logger.info(e)
        old_s.rollback()
    return thing
