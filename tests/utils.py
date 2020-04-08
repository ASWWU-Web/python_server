"""This module contains convenience functions for creating data and inserting it into the databases
   for testing
"""
from contextlib import contextmanager
from datetime import datetime
import csv
from sqlalchemy import Boolean, Column, DateTime, MetaData, String, Table, Integer, ForeignKey, select, MetaData
from sqlalchemy.exc import IntegrityError
import os
import shutil
import glob


def load_csv(csv_file):
    object_list = []
    with open(csv_file) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        headers = next(csv_reader)
        for row in csv_reader:
            row_object = {
                headers[header_index]: row[header_index]
                for header_index in range(0, len(headers))
            }
            object_list.append(row_object)
    return object_list


def replace_databases(from_path, to_path):
    """
    copies clean testing databases into a temporary directory.
    :param from_path:
    :param to_path:
    """
    if not os.path.isdir(to_path):
        os.makedirs(to_path)
    for database in glob.glob(from_path + '/*.db'):
        shutil.copy(database, to_path)

    # # https://stackoverflow.com/a/5003705/11021067
    # from contextlib import closing
    #
    # from src.aswwu.archive_models import ArchiveBase
    # from src.aswwu.models.elections import ElectionBase
    # from src.aswwu.models.forms import JobsBase
    # from src.aswwu.models.mask import Base as MaskBase
    # from src.aswwu.models.pages import PagesBase
    #
    # from src.aswwu.alchemy_new.archive import archive_engine
    # from src.aswwu.alchemy_new.elections import election_engine
    # from src.aswwu.alchemy_new.jobs import jobs_engine
    # from src.aswwu.alchemy_new.mask import engine as mask_engine
    # from src.aswwu.alchemy_new.pages import pages_engine
    #
    # databases = (
    #     (archive_engine, ArchiveBase),
    #     (election_engine, ElectionBase),
    #     (jobs_engine, JobsBase),
    #     (mask_engine, MaskBase),
    #     (pages_engine, PagesBase),
    # )
    # meta = MetaData()

    # for database in databases:
    #     with closing(database[0].connect()) as con:
    #         trans = con.begin()
    #         for table in reversed(database[1].metadata.sorted_tables):
    #             con.execute(table.delete())
    #         trans.commit()





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
        """Generate Mask profiles

        Keyword Arguments:
        number(int) -- The upper limit of generated records (default 5)

        Yields:
        dict        -- Record information

        """
        gender = ["male", "female"]
        majors = ["Computer Science", "Software Engineering", ""]
        pet_peeves = ["Being tinkered with", ""]
        for i in xrange(number):
            #Generates a new username archived.profile0, archived.profile1, etc.
            username = "test.profile" + `i`

            yield {
                "id" : 100 + i,
                "wwuid": 9000000 + i,
                "photo": "profiles/00958-2019687.jpg",
                "majors": majors[i%3],
                "username" : username,
                "gender": gender[i%2],
                "pet_peeves": pet_peeves[i%2]
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


def query_table_elections(conn):
    yield conn.execute(select(ELECTION_TABLE))


def delete_table_elections(conn):
    conn.execute(ELECTION_TABLE.delete())
