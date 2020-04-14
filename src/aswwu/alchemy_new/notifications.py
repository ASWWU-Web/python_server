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
notifications_dbs = sessionmaker(bind=notifications_engine)
notifications_db = notifications_dbs()


# updates a model, or creates it if it doesnt exist
def add_or_update(thing):
    try:
        notifications_db.add(thing)
        notifications_db.commit()
        return thing
    except Exception as e:
        logger.info(e)
        notifications_db.rollback()

def query_notifications(notification_text=None, notification_links=None, start_time=None, end_time=None,
                   severity=None, visible=None):
    """
    Queries the database for notifications matching the specified parameters.
    :param
    :param
    :param
    :param
    :param
    :param
    :param
    :param
    :return: Returns a list of all matched objects in the query.
    """
    thing = None
    try:
        thing = notifications_db.query(notifications_model.Notification)
        if notification_text is not None:
            thing = thing.filter_by(text=str(text))
        if notification_links is not None:
            thing = thing.filter_by(links=str(links))
        if start_time is not None:
            thing = thing.filter_by(notifications_model.Notification.start <= start_before)
        if end_time is not None:
            thing = thing.filter_by(notifications_model.Notification.start >= start_before)
        if severity is not None:
            thing = thing.filter(severity=int(severity))
        if visible is not None:
            thing = thing.filter(visible=int(visible))
        thing = thing.all()
    except Exception as e:
        logger.info(e)
        notifications_db.rollback()
    return thing

