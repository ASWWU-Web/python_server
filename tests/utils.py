"""This module contains convenience functions for creating data and inserting it into the databases
   for testing
"""
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, MetaData, String, Table

from names import get_first_name, get_last_name

METADATA = MetaData()
ASKANYTHING_TABLE = Table('askanythings', METADATA,
                          Column('id', String(50), nullable=False),
                          Column('updated_at', DateTime),
                          Column('question', String(500), nullable=False),
                          Column('reviewed', Boolean),
                          Column('authorized', Boolean))

ASKANYTHING_VOTE_TABLE = Table('askanythingvotes', METADATA,
                               Column('id', String(50), nullable=False),
                               Column(
                                   'question_id', String(50), nullable=False),
                               Column('voter', String(75)))

ELECTION_TABLE = Table('elections', METADATA,
                          Column('id', String(50), nullable=False),
                          Column('wwuid', String(7), nullable=False),
                          Column('candidate_one', String(50)),
                          Column('candidate_two', String(50)),
                          Column('sm_one', String(50)),
                          Column('sm_two', String(50)),
                          Column('new_department', String(150)),
                          Column('district', String(50)),
                          Column('updated_at', DateTime))


def gen_askanythings(number=5):
    """Generate askanythings

    Keyword Arguments:
    number(int) -- The upper limit of generated records (default 5)

    Yields:
    dict        -- Record information

    """
    for i in xrange(number):
        yield {
            "id": i,
            "updated_at": datetime.now(),
            "question": "Something_{}".format(i),
            "reviewed": True,
            "authorized": True
        }


def gen_askanythingvotes(number=5):
    """Generate askanthing votes

    Keyword Arguments:
    number(int) -- The upper limit of generated records (default 5)

    Yields:
    dict        -- Record information

    """
    for i in xrange(number):
        yield {
            "id": i,
            "updated_at": datetime.now(),
            "question_id": 1,
            "voter": get_first_name() + '.' + get_last_name()
        }


def edit(generator, changes):
    """Edit the records produced by a generator and yield result

    Keyword Arguments:
    generator(generator(dict)) -- A generator which yields dicts
    changes(dict)              -- A dictionary of chages to be made

    Yields
    dict                       -- Modified records

    """
    for i, record in enumerate(generator):
        if i in changes.iterkeys():
            record.update(changes[i])

        yield record


@contextmanager
def askanything(conn, askanythings=None):
    """Insert list of records into askanything table

    Keyword Arguments:
    conn(conn)               -- A connection object to the database
    askanythings(list(dict)) -- Records to be inserted into the db (default None)

    """
    if askanythings is None:
        askanythings = list(gen_askanythings())

    conn.execute(ASKANYTHING_TABLE.insert(), askanythings)
    yield askanythings
    conn.execute(ASKANYTHING_TABLE.delete())


@contextmanager
def askanthingvote(conn, askanythingvotes=None):
    """Insert list of records into askanything table

    Keyword Arguments:
    conn(conn)                   -- A connection object to the database
    askanythingvotes(list(dict)) -- Records to be inserted into the db (default None)

    """
    if askanythingvotes is None:
        askanythingvotes = list(gen_askanythingvotes())

    conn.execute(ASKANYTHING_VOTE_TABLE.insert(), askanythingvotes)
    yield askanythingvotes
    conn.execute(ASKANYTHING_VOTE_TABLE.delete())


@contextmanager
def election(conn, elections=None):
    """Insert list of records into elections table

    Keyword Arguments:
    conn(conn)               -- A connection object to the database
    elections(list(dict)) -- Records to be inserted into the db (default None)

    """
    if elections is None:
        elections = list(gen_elections())

    conn.execute(ELECTION_TABLE.insert(), elections)
    yield elections
    conn.execute(ELECTION_TABLE.delete())


def gen_elections(number=5):
    """Generate elections

    Keyword Arguments:
    number(int) -- The upper limit of generated records (default 5)

    Yields:
    dict        -- Record information

    """
    for i in xrange(number):
        yield {
            "id": "{}".format(i),
            "wwuid": "900000{}".format(i),
            "candidate_one": "person_A{}".format(i),
            "candidate_two": "person_B{}".format(i),
            "sm_one": "person_C{}".format(i),
            "sm_two": "person_D{}".format(i),
            "new_department": "department_{}".format(i),
            "district": "district_{}".format(i),
            "updated_at": datetime(2000, 1, 1)
        }
