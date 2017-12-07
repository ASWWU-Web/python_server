import pytest
import threading
import tornado.ioloop
import application
from sqlalchemy import create_engine
from settings import DATABASE


def start_testing_server():
    # pass in the conf default name
    conf_name = "default"

    # initiate the IO loop for Tornado
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.options.parse_config_file("src/aswwu/" + conf_name + ".conf")

    # create thread for running the server
    thread = threading.Thread(
        target=application.start_server, args=(tornado, io_loop))
    thread.daemon = True
    thread.start()

    # allow server to start before running tests
    import time
    time.sleep(1)
    return (io_loop, thread)


def stop_testing_server(io_loop, thread):
    application.stop_server(io_loop)
    # Close the thread
    thread.join()


@pytest.fixture()
def testing_server():
    (io_loop, thread) = start_testing_server()
    yield
    stop_testing_server(io_loop, thread)


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
def archivesdb_conn(scope="module"):
    engine = create_engine(
        'sqlite:///databases/archives.db?check_same_thread=False')
    conn = engine.connect()
    yield conn
    conn.close()
