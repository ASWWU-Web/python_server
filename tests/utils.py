from contextlib import contextmanager
from datetime import datetime
import csv
from sqlalchemy import Boolean, Column, DateTime, MetaData, String, Table, Integer, ForeignKey, select, MetaData
from sqlalchemy.exc import IntegrityError
import os
import shutil
import glob


def load_csv(csv_file, use_unicode=False):
    def create_row_element(headers, row, header_index):
        if use_unicode:
            return unicode(headers[header_index]), unicode(row[header_index]) # change for python 3
        else:
            return headers[header_index], row[header_index]

    object_list = []
    with open(csv_file) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        headers = next(csv_reader)
        for row in csv_reader:
            row_object = dict()
            for header_index in range(0, len(headers)):
                key, value = create_row_element(headers, row, header_index)
                row_object[key] = value
            object_list.append(row_object)
    return object_list


def setup_temp_databases(from_path, to_path):
    """
        copies clean testing databases into a temporary directory.
        :param from_path:
        :param to_path:
        """
    if not os.path.isdir(to_path):
        os.makedirs(to_path)
    else:
        shutil.rmtree(to_path)
        os.makedirs(to_path)
    for database in glob.glob(from_path + '/*.db'):
        shutil.copy(database, to_path)


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
