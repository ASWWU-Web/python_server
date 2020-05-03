from tests.aswwu.behaviors.mask.mask_data import BASE_PROFILE, IMPERSONAL_FIELDS, PERSONAL_FIELDS, SELF_FIELDS
import tests.utils as utils
from tests.aswwu.behaviors.mask.mask_utils import build_profile_dict, assert_update_profile
from tests.aswwu.data.paths import USERS_PATH
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.mask import mask_requests
import json
from settings import testing


def test_update_profile(testing_server):
    users = utils.load_csv(USERS_PATH, use_unicode=True)
    for user in users:
        login_response_text, session = assert_verify_login(user)
        profile_data = build_profile_dict(user)
        assert_update_profile(user, session, profile_data)


def test_search_all(testing_server):
    users = utils.load_csv(USERS_PATH, use_unicode=True)
    expected_results = []
    for user in users:
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
    If a user's privacy is set to 0, then only base info should be returned to a viewer not logged in.
    :return:
    """
    viewee = utils.load_csv(USERS_PATH, use_unicode=True)[0]
    profile_data = build_profile_dict(viewee, {"privacy": "0"})

    viewee_session = assert_verify_login(viewee)[1]
    assert_update_profile(viewee, viewee_session, profile_data)

    profile_response = mask_requests.get_profile(testing["current_year"], viewee["username"])
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
    If a user's privacy is set to 1, then impersonal info should be returned to a viewer not logged in.
    :return:
    """
    viewee = utils.load_csv(USERS_PATH, use_unicode=True)[0]
    profile_data = build_profile_dict(viewee, {"privacy": "1"})

    viewee_session = assert_verify_login(viewee)[1]
    assert_update_profile(viewee, viewee_session, profile_data)

    profile_response = mask_requests.get_profile(testing["current_year"], viewee["username"])

    hidden_keys = SELF_FIELDS.union(PERSONAL_FIELDS).union({"email"})
    expected_profile = build_profile_dict(viewee, {"privacy": "1"}, hidden_keys)

    actual_profile = json.loads(profile_response.text)

    assert profile_response.status_code == 200
    utils.assert_is_equal_sub_dict(expected_profile, actual_profile)
    utils.assert_does_not_contain_keys(actual_profile, hidden_keys)


def test_profile_auth_other(testing_server):
    """
    If a viewer is logged in and views someone else's profile they should receive the view_other model.
    :return:
    """
    viewee, viewer = utils.load_csv(USERS_PATH, use_unicode=True)[0:2]
    profile_data = build_profile_dict(viewee)

    viewee_session = assert_verify_login(viewee)[1]
    assert_update_profile(viewee, viewee_session, profile_data)
    viewer_session = assert_verify_login(viewer)[1]

    profile_response = mask_requests.get_profile(testing["current_year"], viewee["username"], viewer_session)

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
    user = utils.load_csv(USERS_PATH, use_unicode=True)[0]
    profile_data = build_profile_dict(user)

    user_session = assert_verify_login(user)[1]
    assert_update_profile(user, user_session, profile_data)
    profile_response = mask_requests.get_profile(testing["current_year"], user["username"], user_session)

    expected_profile = build_profile_dict(user)
    actual_profile = json.loads(profile_response.text)

    assert profile_response.status_code == 200
    utils.assert_is_equal_sub_dict(expected_profile, actual_profile)
