# mask.py

import logging
from os import getenv

from sqlalchemy import create_engine, func, or_, and_, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import label

import aswwu.models.bases as base
import aswwu.models.mask as mask_model

MaskBase = base.MaskBase
ElectionBase = base.ElectionBase
PagesBase = base.PagesBase
JobsBase = base.JobsBase

logger = logging.getLogger("aswwu")

# defines the databases URLs relative to "server.py"
engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(getenv('DB_USER'),
                                                               getenv('DB_PASSWORD'),
                                                               getenv('DB_IP', '127.0.0.1'),
                                                               getenv('DB_PORT', '3306'),
                                                               getenv('DB_NAME')))
connection = engine.connect()

# bind instances of the databases to corresponding variables
MaskBase.metadata.bind = connection
dbs = sessionmaker(bind=connection)
people_db = dbs()

# create the model tables if they don't already exist
MaskBase.metadata.create_all()


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
    thing = None
    try:
        # thing = people_db.execute("SELECT username, full_name, photo, email, real_views
        #                            FROM (profiles LEFT JOIN (SELECT viewed, SUM(num_views)
        #                            AS real_views
        #                            FROM profileviews
        #                            GROUP BY viewed)
        #                            AS pv
        #                            ON profiles.username = pv.viewed)")
        thing = people_db.query(mask_model.Profile, label("views", func.sum(mask_model.ProfileView.num_views))). \
            join(mask_model.Profile.views). \
            group_by(mask_model.ProfileView.viewed). \
            order_by(desc("views"))
    except Exception as e:
        logger.info(e)
        people_db.rollback()
    return thing


def search_profile_names(query, limit=0):
    thing = None
    try:
        # print('hello')
        thing = people_db.query(mask_model.Profile) \
            .with_entities(mask_model.Profile.username, mask_model.Profile.full_name) \
            .filter(or_(mask_model.Profile.full_name.ilike("%" + query + "%"),
                        mask_model.Profile.username.ilike("%" + query + "%"))) \
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
            group_by(mask_model.ProfileView.viewed). \
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
