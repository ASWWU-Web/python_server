from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import logging
logger = logging.getLogger("aswwu")

Base = declarative_base()
OldBase = declarative_base()

from alchemy.models import *
from alchemy.old_models import *

engine = create_engine("sqlite:///data.db")

Base.metadata.create_all(engine)

Base.metadata.bind = engine
dbs = sessionmaker(bind=engine)

def addOrUpdate(model):
    s = dbs()
    try:
        s.add(model)
        s.commit()
        return model
    except Exception as e:
        logger.info(e)
        s.rollback()

def query_all(model):
    thing = None
    s = dbs()
    try:
        thing = s.query(model).all()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing

def query_by_wwuid(model, wwuid):
    thing = None
    s = dbs()
    try:
        thing = s.query(model).filter_by(wwuid=wwuid).first()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing



old_engine = create_engine("sqlite:////Users/brockhaugen/web/databases/people.db")
OldBase.metadata.bind = old_engine
old_dbs = sessionmaker(bind=old_engine)
def query_old_all(table):
    thing = None
    if table == 'users':
        model = OldUser
    elif table == 'profiles':
        model = OldProfile
    elif table == 'volunteers':
        model = OldVolunteer
    s = old_dbs()
    try:
        thing = s.query(model).all()
    except Exception as e:
        logger.info(e)
        s.rollback()
    return thing
