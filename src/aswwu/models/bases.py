# models.py
import datetime
import logging
import uuid

import six
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger("aswwu")


# create a UUID generator function
def uuid_gen():
    return str(uuid.uuid4())


# define a base model for all other models
class Base(object):
    # every model should also have an ID as a primary key
    # as well as a column indicated when the data was last updated
    id = Column(String(50), primary_key=True, default=uuid_gen)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    # a useful function is being able to call `model.to_json()` and getting valid JSON to send to the user
    def to_json(self, **kwargs):
        obj = {}
        # get the column names of the table
        columns = [str(key).split(".")[1] for key in self.__table__.columns]
        # if called with `model.to_json(skipList=["something"])`
        # then "something" will be added to the list of columns to skip
        skip_list = ['id'] + kwargs.get('skip_list', [])
        # if called similarly to skipList, then only those columns will even be checked
        # by default we check all of the table's columns
        limit_list = kwargs.get('limitList', columns)
        views = kwargs.get('views')
        for key in limit_list:
            if key not in skip_list and key != "views":
                # fancy way of saying "self.key"
                value = getattr(self, key)
                # try to set the value as a utf-8 string
                try:
                    if not isinstance(value, six.string_types):
                        value = str(value)
                    obj[key] = value
                # if that doesn't work set the object to 'None' (output of str(None))
                except Exception as e:
                    obj[key] = 'None'
                    logger.debug("obj[{}] = {} failed to json encode in to_json. Error message: {}".format(key, value, e))
                    pass

            elif key == "views":
                obj[key] = views or str(self.num_views())
        return obj


Base = declarative_base(cls=Base)


class ElectionBase(object):
    # every model should also have an ID as a primary key
    # as well as a column indicated when the data was last updated
    id = Column(String(50), primary_key=True, default=uuid_gen)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    # a useful function is being able to call `model.to_json()` and getting valid JSON to send to the user
    def to_json(self, **kwargs):
        obj = {}
        # get the column names of the table
        columns = [str(key).split(".")[1] for key in self.__table__.columns]
        # if called with `model.to_json(skipList=["something"])`
        # then "something" will be added to the list of columns to skip
        skip_list = ['id'] + kwargs.get('skip_list', [])
        # if called similarly to skipList, then only those columns will even be checked
        # by default we check all of the table's columns
        limit_list = kwargs.get('limit_list', columns)
        for key in limit_list:
            if key not in skip_list:
                # fancy way of saying "self.key"
                value = getattr(self, key)
                # try to set the value as a string, but that doesn't always work
                # NOTE: this should be encoded more properly sometime
                try:
                    obj[key] = str(value)
                except Exception as e:
                    pass
        return obj


ElectionBase = declarative_base(cls=ElectionBase)


class PagesBase(object):
    # every model should also have an ID as a primary key
    # as well as a column indicated when the data was last updated
    id = Column(String(50), primary_key=True, default=uuid_gen)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    # a useful function is being able to call `model.to_json()` and getting valid JSON to send to the user
    # TODO: Make this properly print multilevel lists. (ex. tags, editors)
    def to_json(self, **kwargs):
        obj = {}
        # get the column names of the table
        columns = [str(key).split(".")[1] for key in self.__table__.columns]
        # if called with `model.to_json(skipList=["something"])`
        # then "something" will be added to the list of columns to skip
        skip_list = ['id'] + kwargs.get('skip_list', [])
        # if called similarly to skipList, then only those columns will even be checked
        # by default we check all of the table's columns
        limit_list = kwargs.get('limit_list', columns)
        for key in limit_list:
            if key not in skip_list:
                # fancy way of saying "self.key"
                value = getattr(self, key)
                # try to set the value as a string, but that doesn't always work
                # NOTE: this should be encoded more properly sometime
                try:
                    obj[key] = str(value)
                except Exception as e:
                    pass
        return obj


PagesBase = declarative_base(cls=PagesBase)


class JobsBase(object):
    # every model should also have an ID as a primary key
    # as well as a column indicated when the data was last updated
    id = Column(Integer, primary_key=True)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    # a useful function is being able to call `model.to_json()` and getting valid JSON to send to the user
    # TODO: Make this properly print multilevel lists. (ex. tags, editors)
    def to_json(self, **kwargs):
        obj = {}
        # get the column names of the table
        columns = [str(key).split(".")[1] for key in self.__table__.columns]
        # if called with `model.to_json(skipList=["something"])`
        # then "something" will be added to the list of columns to skip
        skip_list = ['id'] + kwargs.get('skip_list', [])
        # if called similarly to skipList, then only those columns will even be checked
        # by default we check all of the table's columns
        limit_list = kwargs.get('limit_list', columns)
        for key in limit_list:
            if key not in skip_list:
                # fancy way of saying "self.key"
                value = getattr(self, key)
                # try to set the value as a string, but that doesn't always work
                # NOTE: this should be encoded more properly sometime
                try:
                    obj[key] = str(value)
                except Exception as e:
                    pass
        return obj


JobsBase = declarative_base(cls=JobsBase)
