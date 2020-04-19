import requests
from tests.conftest import testing_server
from tests.utils import load_csv
from tests.aswwu.data.paths import USERS_PATH
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.mask import mask_requests
import json


def test_update_profile(testing_server):
    users = load_csv(USERS_PATH)
    for user in users:
        login_response_text, session = assert_verify_login(user)
        profile_fields = {
            "full_name": user["full_name"],
            "email": "someone@somewhere.com",
            "photo": "1819/02523-1234567.jpg",
            "majors": "Computer Science, Mathematics"
        }
        update_response = mask_requests.post_update_profile(user["username"], session, **profile_fields)
        assert update_response.status_code == 200
        print("This test is not complete, it needs to be more thorough.")


def test_search_all(testing_server):
    users = load_csv(USERS_PATH)
    for user in users:
        assert_verify_login(user)
    response = mask_requests.get_search_all()
    assert response.status_code == 200
    expected_text = {
        "results": [
            {"username": "delcie.Lauer", "photo": "None", "email": "None", "full_name": "Delcie Lauer"},
            {"username": "armanda.Woolston", "photo": "None", "email": "None", "full_name": "Armanda Woolston"},
            {"username": "Virgilio.mccraw", "photo": "None", "email": "None", "full_name": "Virgilio Mccraw"},
            {"username": "Holly.garza", "photo": "None", "email": "None", "full_name": "Holly Garza"},
            {"username": "tammie.treacy", "photo": "None", "email": "None", "full_name": "Tammie Treacy"},
            {"username": "Lashay.Semien", "photo": "None", "email": "None", "full_name": "Lashay Semien"},
            {"username": "Melva.woullard", "photo": "None", "email": "None", "full_name": "Melva Woullard"},
            {"username": "Eugene.burnette", "photo": "None", "email": "None", "full_name": "Eugene Burnette"},
            {"username": "raeann.Castor", "photo": "None", "email": "None", "full_name": "Raeann Castor"}
        ]
    }
    print("This test is not complete, profiles should be updated first.")
