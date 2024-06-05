from contextlib import contextmanager
from datetime import datetime
import csv
from sqlalchemy import Boolean, Column, DateTime, MetaData, String, Table, Integer, ForeignKey, select, MetaData
from sqlalchemy.exc import IntegrityError
import os
import shutil
import glob
import settings


def clean_temporary_folder(folder_path=None):
    if folder_path is None:
        folder_path = settings.testing["temporary_files"]
    else:
        assert folder_path.split('/')[0:2] == settings.testing["temporary_files"].split('/')

    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    else:
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)


def setup_databases():
    from_path, to_path = settings.testing['original_testing_databases'], settings.testing['databases_location']
    clean_temporary_folder(folder_path=to_path)
    assert os.path.isdir(from_path) and os.path.isdir(to_path)
    for database in glob.glob(from_path + '/*.db'):
        shutil.copy(database, to_path)


def touch(filename):
    # https://stackoverflow.com/questions/1158076/implement-touch-using-python#comment977269_1158096
    open(filename, 'wa').close()


def reset_databases():
    # https://stackoverflow.com/a/5003705/11021067
    from contextlib import closing

    from src.aswwu.archive_models import ArchiveBase
    from src.aswwu.models.elections import ElectionBase
    from src.aswwu.models.forms import JobsBase
    from src.aswwu.models.mask import Base as MaskBase
    from src.aswwu.models.pages import PagesBase

    from src.aswwu.alchemy_new.archive import archive_engine
    from src.aswwu.alchemy_new.elections import election_engine
    from src.aswwu.alchemy_new.jobs import jobs_engine
    from src.aswwu.alchemy_new.mask import engine as mask_engine
    from src.aswwu.alchemy_new.pages import pages_engine

    databases = (
        (archive_engine, ArchiveBase),
        (election_engine, ElectionBase),
        (jobs_engine, JobsBase),
        (mask_engine, MaskBase),
        (pages_engine, PagesBase),
    )
    meta = MetaData()

    for database in databases:
        with closing(database[0].connect()) as con:
            trans = con.begin()
            for table in reversed(database[1].metadata.sorted_tables):
                con.execute(table.delete())
            trans.commit()

def assert_is_equal_sub_dict(expected, actual):
    """
    Given two python dictionaries, assert that `actual` contains at least the elements in `expected`.
    recurses on sub-dictionaries of `expected`.
    :param actual:
    :param expected:
    :return: bool
    """
    for expected_key, expected_value in expected.items():
        assert expected_key in actual
        if isinstance(expected_value, dict):
            assert_is_equal_sub_dict(expected_value, actual[expected_key])
        else:
            assert actual[expected_key] == expected_value


def assert_does_not_contain_keys(dictionary, keys):
    """
    given a dictionary and a set of string keys, assert that none of the keys are present in the dictionary.

    :param dictionary: a python dictionary
    :param keys: a python set of string keys
    """
    dict_keys = set(dictionary.keys())
    assert dict_keys.intersection(keys) == set()