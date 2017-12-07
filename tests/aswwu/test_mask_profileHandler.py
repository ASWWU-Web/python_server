# test_get_request.py
# Author: Cameron Smith

import requests
import json
from tests.utils import profile, archived_profile, gen_profiles

def test_profile_handler_No_Data(testing_server):

    url = "http://127.0.0.1:8888/1718/test.profile"
    resp = requests.get(url)
    assert (resp.status_code == 404)

def test_profile_handler_current_year(testing_server, peopledb_conn):

    expected_data = {
        "attached_to": "None",
        "birthday": "None",
        "career_goals": "None",
        "class_of": "None",
        "class_standing": "None",
        "department": "None",
        "email": "None",
        "favorite_books": "None",
        #"favorite_food": "None",
        "favorite_movies": "None",
        "favorite_music": "None",
        "full_name": "None",
        "gender": "female",
        "graduate": "None",
        "high_school": "None",
        "hobbies": "None",
        "majors": "Computer Science",
        "minors": "None",
        "office": "None",
        "office_hours": "None",
        "personality": "None",
        "pet_peeves": "None",
        "phone": "None",
        "photo": "profiles/1617/00958-2019687.jpg",
        "preprofessional": "None",
        "privacy": "None",
        "quote": "None",
        "quote_author": "None",
        "relationship_status": "None",
        "username" : "test.profile1",
        "views" : "1",
        "website": "None",
     }

    with profile(peopledb_conn, list(gen_profiles(number = 3))):
        url = "http://127.0.0.1:8888/profile/1718/test.profile1"
        resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


## Define gen_profiles generator function in utils.py

def test_profile_handler_archive(testing_server, archivesdb_conn):

    expected_data = {
        "attached_to": "None",
        "birthday": "None",
        "career_goals": "None",
        "class_of": "None",
        "class_standing": "None",
        "department": "None",
        "email": "None",
        "favorite_books": "None",
        #"favorite_food": "None",
        "favorite_movies": "None",
        "favorite_music": "None",
        "full_name": "None",
        "gender": "female",
        "graduate": "None",
        "high_school": "None",
        "hobbies": "None",
        "majors": "Computer Science",
        "minors": "None",
        "office": "None",
        "office_hours": "None",
        "personality": "None",
        "pet_peeves": "None",
        "phone": "None",
        "photo": "profiles/1617/00958-2019687.jpg",
        "preprofessional": "None",
        "privacy": "None",
        "quote": "None",
        "quote_author": "None",
        "relationship_status": "None",
        "username" : "test.profile1",
        "views" : "None",
        "website": "None",
    }

    with archived_profile(archivesdb_conn, list(gen_profiles(number = 3))):
        url = "http://127.0.0.1:8888/profile/1617/test.profile1"
        resp = requests.get(url)

    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)
