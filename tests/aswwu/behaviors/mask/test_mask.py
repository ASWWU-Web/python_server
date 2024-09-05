from tests.aswwu.behaviors.mask.mask_data import BASE_PROFILE, IMPERSONAL_FIELDS, PERSONAL_FIELDS, SELF_FIELDS, DEFAULT_MASK_PHOTO
import tests.utils as utils
from tests.aswwu.behaviors.mask.mask_utils import build_profile_dict, assert_update_profile
from tests.aswwu.data.users import USERS
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.mask import mask_requests
import json
from settings import  buildMediaPath
import settings

CURRENT_YEAR = settings.config.mask.get('current_year')
PROFILE_PHOTOS_LOCATION = buildMediaPath("profiles")


def test_update_profile(testing_server):
    for user in USERS:
        login_response_text, session = assert_verify_login(user)
        profile_data = build_profile_dict(user)
        assert_update_profile(user, session, profile_data)


def test_search_all(testing_server):
    expected_results = []
    for user in USERS:
        user_session = assert_verify_login(user)[1]
        profile_data = build_profile_dict(user)
        assert_update_profile(user, user_session, profile_data)
        expected_result = dict()
        expected_result.update(user)
        expected_result.update({u"photo": BASE_PROFILE[u"photo"]})
        del(expected_result[u"wwuid"])
        expected_results.append(expected_result)
    all_response = mask_requests.get_search_all()
    expected_results = sorted(expected_results, key=lambda user: user[u"username"])
    actual_results = sorted(json.loads(all_response.text)[u"results"], key=lambda user: user[u"username"])
    assert all_response.status_code == 200
    assert actual_results == expected_results


def test_profile_noauth_private(testing_server):
    """
    If a user's privacy is set to 1, then only base info should be returned to a viewer not logged in.
    :return:
    """
    viewee = USERS[0]
    profile_data = build_profile_dict(viewee, {"privacy": "1"})

    viewee_session = assert_verify_login(viewee)[1]
    assert_update_profile(viewee, viewee_session, profile_data)

    profile_response = mask_requests.get_profile(CURRENT_YEAR, viewee["username"])
    expected_profile = {
        "email": viewee["email"],
        "full_name": viewee["full_name"],
        "photo": BASE_PROFILE["photo"],
        "username": viewee["username"],
    }

    actual_profile = json.loads(profile_response.text)

    assert profile_response.status_code == 200
    utils.assert_is_equal_sub_dict(expected_profile, actual_profile)
    hidden_keys = SELF_FIELDS.union(PERSONAL_FIELDS).union(IMPERSONAL_FIELDS)
    utils.assert_does_not_contain_keys(actual_profile, hidden_keys)


def test_profile_noauth_public(testing_server):
    """
    If a user's privacy is set to 0, then impersonal info should be returned to a viewer not logged in.
    :return:
    """
    viewee = USERS[0]
    profile_data = build_profile_dict(viewee, {"privacy": "0"})

    viewee_session = assert_verify_login(viewee)[1]
    assert_update_profile(viewee, viewee_session, profile_data)

    profile_response = mask_requests.get_profile(CURRENT_YEAR, viewee["username"])

    hidden_keys = SELF_FIELDS.union(PERSONAL_FIELDS).union({"email"})
    expected_profile = build_profile_dict(viewee, {"privacy": "0"}, hidden_keys)

    actual_profile = json.loads(profile_response.text)

    assert profile_response.status_code == 200
    utils.assert_is_equal_sub_dict(expected_profile, actual_profile)
    utils.assert_does_not_contain_keys(actual_profile, hidden_keys)

def test_profile_auth_other(testing_server):
    """
    If a viewer is logged in and views someone else's profile they should receive the view_other model.
    :return:
    """
    viewee, viewer = USERS[0:2]
    profile_data = build_profile_dict(viewee)

    viewee_session = assert_verify_login(viewee)[1]
    assert_update_profile(viewee, viewee_session, profile_data)
    viewer_session = assert_verify_login(viewer)[1]

    profile_response = mask_requests.get_profile(CURRENT_YEAR, viewee["username"], viewer_session)

    hidden_keys = SELF_FIELDS
    expected_profile = build_profile_dict(viewee, remove_keys=hidden_keys)
    actual_profile = json.loads(profile_response.text)

    assert profile_response.status_code == 200
    utils.assert_is_equal_sub_dict(expected_profile, actual_profile)
    utils.assert_does_not_contain_keys(actual_profile, hidden_keys)


def test_profile_auth_self(testing_server):
    """
    If a viewer is logged in and views their own profile they should receive the whole profile model.
    :return:
    """
    user = USERS[0]
    profile_data = build_profile_dict(user)

    user_session = assert_verify_login(user)[1]
    assert_update_profile(user, user_session, profile_data)
    profile_response = mask_requests.get_profile(CURRENT_YEAR, user["username"], user_session)

    expected_profile = build_profile_dict(user)
    actual_profile = json.loads(profile_response.text)

    assert profile_response.status_code == 200
    utils.assert_is_equal_sub_dict(expected_profile, actual_profile)


def test_search_names(testing_server):
    users = USERS
    for user in users:
        assert_verify_login(user)

    empty_response_query = "abcd"
    expected_empty_response = []
    empty_query_response = mask_requests.get_search_names_fast(name_query=empty_response_query)
    actual_empty_response = json.loads(empty_query_response.text)["results"]
    assert empty_query_response.status_code == 200
    assert len(actual_empty_response) == 0
    assert actual_empty_response == expected_empty_response

    many_response_query = "e"
    expected_many_response = [
        {'username': 'delcie.Lauer',    'full_name': 'Delcie Lauer'},
        {'username': 'Eugene.burnette', 'full_name': 'Eugene Burnette'},
        {'username': 'Lashay.Semien',   'full_name': 'Lashay Semien'},
        {'username': 'Melva.woullard',  'full_name': 'Melva Woullard'},
        {'username': 'raeann.Castor',   'full_name': 'Raeann Castor'},
    ]
    many_query_response = mask_requests.get_search_names_fast(name_query=many_response_query)
    actual_many_response = json.loads(many_query_response.text)["results"]
    assert many_query_response.status_code == 200
    assert len(actual_many_response) == len(expected_many_response)
    expected_many_response = sorted(expected_many_response, key=lambda user: user["username"])
    actual_many_response = sorted(actual_many_response, key=lambda user: user["username"])
    assert actual_many_response == expected_many_response

    unique_response_query = "arm"
    expected_unique_response = [{"username": "armanda.Woolston", "full_name": "Armanda Woolston"}]
    unique_query_response = mask_requests.get_search_names_fast(name_query=unique_response_query)
    actual_unique_response = json.loads(unique_query_response.text)["results"]
    assert unique_query_response.status_code == 200
    assert len(actual_unique_response) == 1
    assert actual_unique_response == expected_unique_response

# TODO fix this test
# def test_list_photos(testing_server):
#     users = USERS[0:3]

#     photos = [
#         settings.environment["current_year"] + "/a01-" + users[1]["wwuid"] + ".jpg",
#         settings.environment["current_year"] + "/a02-" + users[2]["wwuid"] + ".jpg",
#                                       "1718" + "/a03-" + users[2]["wwuid"] + ".jpg",
#     ]

#     distutils.dir_util.create_tree(settings.environment["profile_photos_location"], photos)
#     for photo in photos:
#         utils.touch(settings.environment["profile_photos_location"] + "/" + photo)

#     expected_empty_photos = []
#     session = assert_verify_login(users[0])[1]
#     empty_response = mask_requests.get_list_profile_photos(session)
#     actual_empty_response = json.loads(empty_response.text)["photos"]
#     assert empty_response.status_code == 200
#     assert actual_empty_response == expected_empty_photos

#     expected_many_photos = ["profiles/" + photo for photo in photos[1:3]]
#     session = assert_verify_login(users[2])[1]
#     many_response = mask_requests.get_list_profile_photos(session)
#     actual_many_response = json.loads(many_response.text)["photos"]
#     assert many_response.status_code == 200
#     assert len(actual_many_response) == 2
#     assert set(actual_many_response) == set(expected_many_photos)


def test_search_profiles(testing_server):
    users = USERS
    for user in users[0:4]:
        session = assert_verify_login(user)[1]
        profile_data = build_profile_dict(user)
        assert_update_profile(user, session, profile_data)

    for user in users[4:8]:
        session = assert_verify_login(user)[1]
        profile_data = build_profile_dict(user)
        profile_data.update({"majors": "Physics"})
        assert_update_profile(user, session, profile_data)

    physics_nursing_user = users[8]
    session = assert_verify_login(physics_nursing_user)[1]
    profile_data = build_profile_dict(physics_nursing_user)
    profile_data.update({"majors": "Physics,Nursing"})
    assert_update_profile(physics_nursing_user, session, profile_data)

    expected_search_response = [{
        "username": user["username"],
        "photo": DEFAULT_MASK_PHOTO,
        "email": user["email"],
        "full_name": user["full_name"],
    } for user in users[4:9]]
    search_response = mask_requests.get_profile_search(CURRENT_YEAR, dictionary_query={"majors": "physics"})
    assert search_response.status_code == 200
    actual_search_response = json.loads(search_response.text)["results"]
    for result in actual_search_response:
        assert result in expected_search_response
    assert len(actual_search_response) == len(expected_search_response)
