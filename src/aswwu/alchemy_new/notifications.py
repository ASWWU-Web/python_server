# notifications.py

#import and set up the logging

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload

import src.aswwu.models.bases as base
from settings import database

NotificationsBase = base.NotificationsBase

logger = logging.getLogger("aswwu")

notifications_engine = create_engine("sqlite:///" + database['location'] + "/notifications.db")

NotificationsBase.metadata.create_all(notifications_engine)

# bind instances of the databases to corresponding variables
NotificationsBase.metadata.bind = notifications_engine
notifications_dbs = sessionmaker(bind=jobs_engine)
notifications_db = notifications_dbs()


# updates a model, or creates it if it doesnt exist
def add_or_update_notification(thing):
    try:
        notifications_db.add(thing)
        notifications_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        notifications_db.rollback()

# TODO decide how to query specific notifications

#def query_by_notification_(model, name):
#    thing = None
#    try:
#        thing = jobs_db.query(model).options(joinedload('*')).filter_by(job_name=str(name)).all()
#    except Exception as e:
#        logger.info(e)
#        jobs_db.rollback()
#    return thing
#
#
#def query_all_forms(model):
#    thing = None
#    try:
#        thing = jobs_db.query(model).all()
#    except Exception as e:
#        logger.info(e)
#        jobs_db.rollback()
#    return thing
#
#
## permanently deletes a given model
#def delete_thing_forms(thing):
#    try:
#        jobs_db.delete(thing)
#        jobs_db.commit()
#    except Exception as e:
#        logger.info(e)
#        jobs_db.rollback()
