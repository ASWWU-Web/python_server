# mask.py

import logging

from sqlalchemy import create_engine, func, or_, and_, desc, asc, case
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import label

import aswwu.models.bases as base
import aswwu.models.mask as mask_model


Base = base.Base
ElectionBase = base.ElectionBase
PagesBase = base.PagesBase
JobsBase = base.JobsBase

logger = logging.getLogger("aswwu")

# defines the databases URLs relative to "server.py"
engine = create_engine("sqlite:///../databases/people.db")

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
        profiles = people_db.query(mask_model.Profile)\
            .join(mask_model.User, mask_model.Profile.username == mask_model.User.username)\
            .group_by(mask_model.User.username)\
            .order_by(asc(
                case(
                    [
                        (mask_model.Profile.photo == 'None', 2),
                        (mask_model.Profile.photo == '', 2),
                        (mask_model.Profile.photo == None, 2),
                        (mask_model.Profile.photo == 'images/default_mask/default.jpg', 2)
                    ], else_=1)), func.random())

    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return profiles


def search_profile_names(query, limit=0):
    thing = None
    try:
        # print('hello')
        thing = people_db.query(mask_model.Profile) \
            .with_entities(mask_model.Profile.username, mask_model.Profile.full_name) \
            .filter(or_(mask_model.Profile.full_name. ilike("%" + query + "%"), mask_model.Profile.username. ilike("%" + query + "%"))) \
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
        search_statement = and_(search_term_generator(search_criteria))
        thing = people_db.query(mask_model.Profile, label("views", func.sum(mask_model.ProfileView.num_views))). \
            filter(search_statement). \
            join(mask_model.Profile.views). \
            group_by(mask_model.ProfileView.viewed).\
            order_by(desc("views"))
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


def num_views(username):
    thing = None
    try:
        thing = people_db.query(label("views", func.sum(mask_model.ProfileView.num_views))). \
            group_by(mask_model.ProfileView.viewed). \
            filter(mask_model.ProfileView.viewed == username)
        try:
            thing = thing.one().views
        except Exception:
            thing = None
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


# finds a single user by their username
def query_by_username(username):
    thing = None
    try:
        thing = people_db.query(mask_model.User).filter_by(username=str(username)).one()
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
