import pytest
import threading
import tornado.ioloop
from tornado.options import options
from src import application
from sqlalchemy import create_engine
from settings import database as DATABASE
from src.application import Application
from tests.utils import query_table_elections, delete_table_elections


def start_testing_server():
    # pass in the conf default name
    conf_file = "tests/default.conf"
    tornado.options.parse_config_file(conf_file)

    io_loop = tornado.ioloop.IOLoop.instance()

    application = Application()
    application.listen(options.port)

    # create thread for running the server
    thread = threading.Thread(
        target=application.start_server, args=(tornado, io_loop))
    thread.daemon = True
    thread.start()

    # allow server to start before running tests
    import time
    time.sleep(1)
    return io_loop


def stop_testing_server(io_loop):
    application.stop_server(io_loop)


@pytest.fixture()
def testing_server():
    io_loop = start_testing_server()
    yield
    stop_testing_server(io_loop)


@pytest.fixture()
def peopledb_conn(scope="module"):
    engine = create_engine(
        'sqlite://' + DATABASE['location'] + '/people.db?check_same_thread=False')
    conn = engine.connect()
    yield conn
    conn.close()


@pytest.fixture()
def jobsdb_conn(scope="module"):
    """
    Create connection to the jobs database
    """
    engine = create_engine(
        'sqlite:///databases/jobs.db?check_same_thread=False')
    conn = engine.connect()
    yield conn
    conn.close()


@pytest.fixture()
def electiondb_conn(scope="module"):
    engine = create_engine(
        'sqlite:///databases/senate_elections.db?check_same_thread=False')
    conn = engine.connect()
    yield conn
    conn.close()


@pytest.fixture()
def db_query(electiondb_conn):
    yield query_table_elections(electiondb_conn)
    delete_table_elections(electiondb_conn)


@pytest.fixture()
def archivesdb_conn(scope="module"):
    engine = create_engine(
        'sqlite:///databases/archives.db?check_same_thread=False')
    conn = engine.connect()
    yield conn
    conn.close()
