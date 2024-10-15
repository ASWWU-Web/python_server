# mask.py

import logging
from typing import TypeVar

from sqlalchemy import create_engine, func, or_, and_, asc, case, select
from sqlalchemy.orm import sessionmaker

import src.aswwu.models.bases as base
import src.aswwu.models.mask as mask_model
from settings import config


Base = base.Base
# ElectionBase = base.ElectionBase
# PagesBase = base.PagesBase
# JobsBase = base.JobsBase

logger = logging.getLogger(config.logging.get('log_name'))

# defines the databases URLs relative to "server.py"
engine = create_engine("sqlite:///" + config.database.get('databases') + "/people.db")

# bind instances of the databases to corresponding variables
Base.metadata.bind = engine
dbs = sessionmaker(bind=engine)
people_db = dbs()


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


def search_all_profiles():
    profiles = None
    try:
        # https://stackoverflow.com/questions/28872013/how-to-order-by-case-descending
            profiles_statement = select(mask_model.Profile.username, 
                                        mask_model.Profile.full_name, 
                                        mask_model.Profile.photo, 
                                        mask_model.Profile.email)\
            .join(mask_model.User, mask_model.Profile.username == mask_model.User.username)\
            .group_by(mask_model.User.username)\
            .order_by(asc(
                case(
                    
                        (mask_model.Profile.photo == 'None', 2),
                        (mask_model.Profile.photo == '', 2),
                        (mask_model.Profile.photo == None, 2),
                        (mask_model.Profile.photo == 'images/default_mask/default.jpg', 2)
                    , else_=1)), func.random())
            profiles = people_db.execute(profiles_statement).all()

    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return profiles


def search_profile_names(query, limit=0):
    thing = None
    try:
        thing = people_db.query(mask_model.Profile) \
            .with_entities(mask_model.Profile.username, mask_model.Profile.full_name) \
            .filter(or_(mask_model.Profile.full_name.ilike(f"%{query}%"), mask_model.Profile.username.ilike(f"%{query}%"))) \
            .order_by(mask_model.Profile.full_name) \
            .limit(limit) \
            .all()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


def multiple_criteria_generator(key, criteria):
    for status in criteria.split(","):
        yield getattr(mask_model.Profile, key).ilike("%" + status + "%")


def search_term_generator(search_criteria):
    for key in search_criteria:
        if key == "gender":
            yield mask_model.Profile.gender.ilike(search_criteria["gender"])
        elif key == "username" or key == "full_name":
            yield and_(mask_model.Profile.username.ilike("%" + search_criteria[key] + "%") +
                       mask_model.Profile.full_name.ilike("%" + search_criteria[key] + "%"))
        else:
            if "," not in search_criteria[key]:
                yield getattr(mask_model.Profile, key).ilike("%" + search_criteria[key] + "%")
            else:
                yield or_(multiple_criteria_generator(key, search_criteria[key]))


def search_profiles(search_criteria):
    thing = None
    try:
        select_statement = select(
            mask_model.Profile.username, 
            mask_model.Profile.full_name, 
            mask_model.Profile.photo, 
            mask_model.Profile.email
        ).where(and_(search_term_generator(search_criteria)))
        thing = people_db.execute(select_statement).all()
    except Exception as e:
        logger.error(e)
        people_db.rollback()
    return thing

# finds all rows for a given model matching the given WWUID
def query_by_wwuid(model, wwuid: str):
    try:
        stmt = select(model).filter_by(wwuid=str(wwuid))
        thing = people_db.execute(stmt).all()
        return thing[0]
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return [] 
    


# finds a single user by their username
def query_by_username(username):
    thing = None
    try:
        thing = people_db.query(mask_model.User).filter_by(username=str(username)).one()
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
        # get first element of the list and tuple
        return thing[0]
    return thing


# permanently deletes a given model
def delete_thing(thing):
    try:
        people_db.delete(thing)
        people_db.commit()
    except Exception as e:
        logger.info(e)
        people_db.rollback()
