import requests
import json
from tests.utils import profile, archived_profile, gen_profiles


def test_search_specific_current(testing_server, peopledb_conn):
    expected_data = {
        'results': [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile1',
            'views':'1'
        }]
    }
    with profile(peopledb_conn, list(gen_profiles(number = 3))):
        url = "http://127.0.0.1:8888/search/1718/test.profile1"
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_search_specific_archive(testing_server, archivesdb_conn):
    expected_data = {
        'results': [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile1',
            'views':'None'
        }]
    }
    with archived_profile(archivesdb_conn, list(gen_profiles(number = 3))):
        url = "http://127.0.0.1:8888/search/1617/test.profile1"
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_search_single_letter_current(testing_server, peopledb_conn):
    expected_data = {
        "results": [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile0',
            'views':'0'
        },{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile1',
            'views':'1'
        },{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile2',
            'views':'0'
        }]
    }
    with profile(peopledb_conn, list(gen_profiles(number = 3))):
        url = 'http://127.0.0.1:8888/search/1718/t'
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_search_all_current(testing_server, peopledb_conn):
    expected_data = {
        "results": [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile0',
            'views':'0'
        },{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile1',
            'views':'1'
        },{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile2',
            'views':'0'
        }]
    }

    with profile(peopledb_conn, list(gen_profiles(number = 3))):
        url = 'http://127.0.0.1:8888/search/all'
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_search_single_letter_archive(testing_server, archivesdb_conn):
    expected_data = {
        "results": [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile0',
            'views':'None'
        },{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile1',
            'views':'None'
        },{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile2',
            'views':'None'
        }]
    }

    with archived_profile(archivesdb_conn, list(gen_profiles(number = 3))):
        url = 'http://127.0.0.1:8888/search/1617/t'
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_NotFound(testing_server, peopledb_conn):
    expected_data = {'results': []}
    with profile(peopledb_conn, list(gen_profiles(number = 3))):
        url = 'http://127.0.0.1:8888/search/1718/d'
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_search_subgroup_current(testing_server, peopledb_conn):
    expected_data = {
        'results': [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile1',
            'views':'1'
        },{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile10',
            'views':'0'
        }]}
    with profile(peopledb_conn, list(gen_profiles(number = 11))):
        url = 'http://127.0.0.1:8888/search/1718/e1'
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_search_subgroup_archive(testing_server, archivesdb_conn):
    expected_data = {
        'results': [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile2',
            'views':'None'
        },{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile20',
            'views':'None'
        }]}
    with archived_profile(archivesdb_conn, list(gen_profiles(number = 21))):
        url = 'http://127.0.0.1:8888/search/1617/e2'
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)

def test_search_female_archives(testing_server, archivesdb_conn):
    expected_data = {
        'results': [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile1',
            'views':'None'
        }]}
    with archived_profile(archivesdb_conn, list(gen_profiles(number = 2))):
        url = 'http://127.0.0.1:8888/search/1617/gender=female'
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)

def test_search_major_and_male_archive(testing_server, archivesdb_conn):
    expected_data = {
        'results': [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile0',
            'views':'None'
        }]}
    with archived_profile(archivesdb_conn, list(gen_profiles(number = 1))):
        url = 'http://127.0.0.1:8888/search/1617/majors=Computer;gender=male'
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)

def test_search_major_and_female_current(testing_server, peopledb_conn):
    expected_data = {
        'results': [{
            'email':'None',
            'full_name':'None',
            'photo':'profiles/00958-2019687.jpg',
            'username':'test.profile1',
            'views':'1'
        }]}
    with profile(peopledb_conn, list(gen_profiles(number = 2))):
        url = 'http://127.0.0.1:8888/search/1718/gender=female;majors=Software'
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)
