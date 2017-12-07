"""This module contains convenience functions for creating data and inserting it into the databases
   for testing
"""
from contextlib import contextmanager
from datetime import datetime


from sqlalchemy import Boolean, Column, DateTime, MetaData, String, Table, Integer, ForeignKey
from sqlalchemy.exc import IntegrityError

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

PROFILES_TABLE = Table('profiles', METADATA,
                        Column('id', String(50), primary_key=True),
                        Column('wwuid', String(10), nullable=False),
                        Column('photo', String(250)),
                        Column('majors', String(500)),
                        Column('username', String(105)),
                        Column('gender', String(250)))

PROFILES1617_TABLE = Table('profiles1617', METADATA,
                        Column('id', String(50), primary_key=True),
                        Column('wwuid', String(10), nullable=False),
                        Column('photo', String(250)),
                        Column('majors', String(500)),
                        Column('username', String(105)),
                        Column('gender', String(250)))

JOB_POSTING_TABLE = Table(
    'jobforms', METADATA,
    Column('id', Integer(), nullable=False),
    Column('job_name', String(100), nullable=False),
    Column('job_description', String(10000)),
    Column('department', String(150)),
    Column('visibility', Boolean, default=False),
    Column('owner', String(100), nullable=False),
    Column('image', String(100), nullable=False)
)

JOB_QUESTION_TABLE = Table(
    'jobquestions', METADATA,
    Column('id', Integer(), nullable=False),
    Column('question', String(5000)),
    Column('jobID', String(50), ForeignKey('jobforms.id'))
)

JOB_APPLICATION_TABLE = Table(
    'jobapplications', METADATA,
    Column('id', Integer(), nullable=False),
    Column('jobID', String(50), ForeignKey('jobforms.id')),
    Column('username', String(100), nullable=False),
    Column('status', String(50))
)

JOB_ANSWER_TABLE = Table(
    'jobanswers', METADATA,
    Column('id', Integer(), nullable=False),
    Column('questionID', String(50), ForeignKey('jobquestions.id')),
    Column('answer', String(10000)),
    Column('applicationID', String(50), ForeignKey('jobapplications.id'))
)

ELECTION_TABLE = Table(
    'elections', METADATA,
    Column('id', String(50), nullable=False),
    Column('wwuid', String(7), nullable=False),
    Column('candidate_one', String(50)),
    Column('candidate_two', String(50)),
    Column('sm_one', String(50)),
    Column('sm_two', String(50)),
    Column('new_department', String(150)),
    Column('district', String(50)),
    Column('updated_at', DateTime)
)


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
    """Generate askanything votes

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


# Generator to create archived user profiles
def gen_profiles(number=5):
        """Generate Mask profilesaskanythings

        Keyword Arguments:
        number(int) -- The upper limit of generated records (default 5)

        Yields:
        dict        -- Record information

        """
        for i in xrange(number):
            username = "test.profile"
            username += `i`

            yield {
                "id" : 100 + i,
                "wwuid": 9000000 + i,
                "photo": "profiles/1617/00958-2019687.jpg",
                "majors": "Computer Science",
                "username" : username, #Generates a new username archived.profile0, archived.profile1, etc.
                "gender": "female"
        }


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
def archived_profile(conn, profiles=None):
    """Insert list of records into profile table

    Keyword Arguments:
    conn(conn)               -- A connection object to the database
    profiles(list(dict))     -- Records to be inserted into the db (default None)

    """
    if profiles is None:
        profiles = list(gen_profiles())

    conn.execute(PROFILES1617_TABLE.insert(), profiles)
    yield profiles
    conn.execute(PROFILES1617_TABLE.delete())


@contextmanager
def profile(conn, profiles=None):
    """Insert list of records into profile table

    Keyword Arguments:
    conn(conn)               -- A connection object to the database
    profiles(list(dict))     -- Records to be inserted into the db (default None)

    """
    if profiles is None:
        profiles = list(gen_profiles())

    conn.execute(PROFILES_TABLE.insert(), profiles)
    yield profiles
    conn.execute(PROFILES_TABLE.delete())

def gen_job_posting(number=5):
    """
    Generator for job postings
    """
    for i in xrange(2, number + 2):
        yield {
            "id": i,
            "job_name": "Job number {}".format(i),
            "job_description": "A description for the job",
            "department": "department {}".format(i),
            "visibility": 0,
            "owner": get_first_name() + '.' + get_last_name(),
            "image": "/images/{}".format(i)
        }


def gen_job_answer(number_answers_per_app=5, num_apps=5):
    """
    Generator for job answers
    """
    for i in xrange(1, number_answers_per_app * num_apps + 2):
        yield {
            "id": i,
            "question": "Question Number {}".format(i),
            "jobID": i % (num_apps) + 1
        }


def gen_job_app(number_apps_per_job=5, num_postings=5):
    """
    Generator for job applications
    """
    for i in xrange(1, number_apps_per_job * num_postings + 1):
        yield {
            "id": i,
            "jobID": i % num_postings + 1,
            "username": get_first_name() + '.' + get_last_name(),
            "status": ["new", "reviewed", "hire", "no"][i % 4]
        }


def gen_job_question(number_questions_per_posting=5, num_postings=5):
    """
    Generator for job questions
    """
    for i in xrange(18, number_questions_per_posting * num_postings + 18):
        yield {
            "id": i,
            "question": "Question Number {}".format(i),
            "jobID": i % (num_postings) + 2
        }


@contextmanager
def job_application(conn, job_apps=None):
    """
    Performs insertion of job applications into database
    """
    job_apps = job_apps or list(gen_job_app())

    try:
        conn.execute(JOB_APPLICATION_TABLE.insert(), job_apps)
        conn.execute(JOB_APPLICATION_TABLE.insert(), {
            "id": 0,
            "jobID": 1,
            "username": "ryan.rabello",
            "status": "reviewed"
        })
    except IntegrityError:
        conn.execute(JOB_APPLICATION_TABLE.delete())
        conn.execute(JOB_APPLICATION_TABLE.insert(), {
            "id": 0,
            "jobID": 1,
            "username": "ryan.rabello",
            "status": "reviewed"
        })
        conn.execute(JOB_APPLICATION_TABLE.insert(), job_apps)
    yield job_apps
    conn.execute(JOB_APPLICATION_TABLE.delete())


@contextmanager
def job_answer(conn, job_answers=None):
    """
    Performs insertion of job answers into database
    """
    job_answers = job_answers or list(gen_job_answer())

    try:
        conn.execute(JOB_ANSWER_TABLE.insert(), job_answers)
    except IntegrityError:
        conn.execute(JOB_ANSWER_TABLE.delete())
        conn.execute(JOB_ANSWER_TABLE.insert(), job_answers)
    yield job_answers
    conn.execute(JOB_ANSWER_TABLE.delete())


@contextmanager
def job_posting(conn, job_postings=None):
    """
    Performs insertion of job postings into database
    """
    job_postings = job_postings or list(gen_job_posting())

    try:
        conn.execute("INSERT INTO jobforms (id, job_name, job_description,\
            visibility, owner, image) VALUES (1, 'ASWWU Generic',\
            \"Doesn't Really Matter\", 0, 'ryan.rabello', '')")
        conn.execute(JOB_POSTING_TABLE.insert(), job_postings)
    except IntegrityError:
        conn.execute(JOB_POSTING_TABLE.delete())
        conn.execute("INSERT INTO jobforms (id, job_name, job_description,\
            visibility, owner, image) VALUES (1, 'ASWWU Generic',\
            \"Doesn't Really Matter\", 0, 'ryan.rabello', '')")
        conn.execute(JOB_POSTING_TABLE.insert(), job_postings)
    yield job_postings
    conn.execute(JOB_POSTING_TABLE.delete())


@contextmanager
def job_question(conn, job_questions=None):
    """
    Performs insertion of job questions into database
    """
    job_questions = job_questions or list(gen_job_question())
    questions = [
        "First Name",
        "Last Name",
        "WWU ID#",
        "Phone Number",
        "E-mail",
        "On-Campus Address",
        "High-School Attended",
        "",
        "",
        "Current SM/ ACA?",
        "If so, where?",
        "On average, how many credits will you be taking?",
        "How many hours do you hope to work?",
        "Have you worked for ASWWU before? If so, what job?",
        "What other jobs or responsibilities will require your attention/ time?",
        "Why do you want to work for ASWWU?",
        "If there was one thing you could change about ASWWU, what would it be?"
    ]
    try:
        for i in xrange(1, 18):
            if i not in [8, 9]:
                conn.execute("INSERT INTO jobquestions (id, question, jobID)\
                    VALUES ({}, '{}', {})".format(i, questions[i - 1], 1))
        conn.execute(JOB_QUESTION_TABLE.insert(), job_questions)
    except IntegrityError:
        conn.execute(JOB_QUESTION_TABLE.delete())
        for i in xrange(1, 18):
            if i not in [8, 9]:
                conn.execute("INSERT INTO jobquestions (id, question, jobID)\
                    VALUES ({}, '{}', {})".format(i, questions[i - 1], 1))
        conn.execute(JOB_QUESTION_TABLE.insert(), job_questions)
    yield job_questions
    conn.execute(JOB_QUESTION_TABLE.delete())


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
