# models.py

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Text
import uuid
import datetime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
import hashlib
from pattern.en import pluralize


# create a UUID generator function
def uuid_gen():
    return str(uuid.uuid4())


# define a base model for all other models
class Base(object):
    @declared_attr
    def __tablename__(self):
        # every model will have a corresponding table that is the lowercase and pluralized version of it's name
        return pluralize(self.__name__.lower())

    # every model should also have an ID as a primary key
    # as well as a column indicated when the data was last updated
    id = Column(String(50), primary_key=True, default=uuid_gen)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now())

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
        for key in limit_list:
            if key not in skip_list and key != "views":
                # fancy way of saying "self.key"
                value = getattr(self, key)
                # try to set the value as a string, but that doesn't always work
                # NOTE: this should be encoded more properly sometime
                try:
                    obj[key] = str(value)
                except Exception as e:
                    # This tries to leave the string in unicode if it cannot be converted using str()
                    # NOTE: This should also be done more properly sometime
                    try:
                        obj[key] = value.encode("utf-8")
                    except Exception as e:
                        # Oh well
                        pass


            elif key == "views":
                obj[key] = str(self.num_views())
        return obj


Base = declarative_base(cls=Base)


class ElectionBase(object):
    @declared_attr
    def __tablename__(self):
        # every model will have a corresponding table that is the lowercase and pluralized version of it's name
        return pluralize(self.__name__.lower())

    # every model should also have an ID as a primary key
    # as well as a column indicated when the data was last updated
    id = Column(String(50), primary_key=True, default=uuid_gen)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

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
    @declared_attr
    def __tablename__(self):
        # every model will have a corresponding table that is the lowercase and pluralized version of it's name
        return pluralize(self.__name__.lower())

    # every model should also have an ID as a primary key
    # as well as a column indicated when the data was last updated
    id = Column(String(50), primary_key=True, default=uuid_gen)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

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
    @declared_attr
    def __tablename__(self):
        # every model will have a corresponding table that is the lowercase and pluralized version of it's name
        return pluralize(self.__name__.lower())

    # every model should also have an ID as a primary key
    # as well as a column indicated when the data was last updated
    id = Column(Integer, primary_key=True)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

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
