from contextlib import contextmanager
from sqlalchemy import Table, Column, String, MetaData, DateTime, Boolean
from datetime import datetime

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

ASKANYTHINGS_DATA = [{
    "id": 1,
    "updated_at": datetime.now(),
    "question": "Something",
    "reviewed": True,
    "authorized": True
}, {
    "id": 2,
    "updated_at": datetime.now(),
    "question": "Something Else",
    "reviewed": True,
    "authorized": True
}, {
    "id": 3,
    "updated_at": datetime.now(),
    "question": "Something More",
    "reviewed": True,
    "authorized": True
}]

ASKANYTHINGVOTES_DATA = [{
    "id": 1,
    "updated_at": datetime.now(),
    "question_id": 1,
    "voter": "ryan.rabello"
}, {
    "id": 2,
    "updated_at": datetime.now(),
    "question_id": 2,
    "voter": "ryan.rabello"
}, {
    "id": 3,
    "updated_at": datetime.now(),
    "question_id": 3,
    "voter": "ryan.rabello"
}]


@contextmanager
def askanything(conn, askanythings=ASKANYTHINGS_DATA):
    conn.execute(ASKANYTHING_TABLE.insert(), askanythings)
    yield askanythings
    conn.execute(ASKANYTHING_TABLE.delete())


@contextmanager
def askanthingvote(conn, askanythingvotes=ASKANYTHINGVOTES_DATA):
    conn.execute(ASKANYTHING_VOTE_TABLE.insert(), askanythingvotes)
    yield askanythingvotes
    conn.execute(ASKANYTHING_VOTE_TABLE.delete())


def gen_askanythings(number=5):
    arr = []
    for i in number:
        arr.push({
            "id": i,
            "updated_at": datetime.now(),
            "question": "Something_{}".format(i),
            "reviewed": True,
            "authorized": True
        })
