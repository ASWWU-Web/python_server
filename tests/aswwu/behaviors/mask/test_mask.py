import requests
from tests.conftest import testing_server
import tests.utils as utils
from tests.aswwu.data.paths import USERS_PATH
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.mask import mask_requests
import json
from settings import testing
import requests


BASE_PROFILE = {
        u'attached_to': u'Some Name',
        u'birthday': u'01-01',
        u'career_goals': u'Web Development',
        u'class_of': u'2020',
        u'class_standing': u'Senior',
        u'department': u'None',
        u'email': u'armanda.Woolston@wallawalla.edu',
        u'favorite_books': u'Clean Architecture',
        u'favorite_food': u'Byte size snacks',
        u'favorite_movies': u'Some Movie',
        u'favorite_music': u'Some Music',
        u'gender': u'Other',
        u'graduate': u'No',
        u'high_school': u'SomePlace High',
        u'hobbies': u'Test Driven Development',
        u'majors': u'Computer Science',
        u'minors': u'Web Design and Development',
        u'office': u'None',
        u'office_hours': u'None',
        u'personality': u'ABCD',
        u'pet_peeves': u'Broken Code',
        u'phone': u'111-111-1111',
        u'photo': u'images/default_mask/default.jpg',
        u'preprofessional': u'No',
        u'privacy': u'1',
        u'quote': u'A looooooooooooooooooooooooooooooooooooooooooooooooo'
                  u'ooooooooooooooooooooooooooooonnnnnnnnnnnnnnnnnnnnnnn'
                  u'nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnngg'
                  u'ggggggggggggggggggggggg string of text with some wei'
                  u'rd chars !@#$%&amp;*()_+-=`~?&gt;&lt;|}{\\][\';": an'
                  u'd a second " plus a newline\n\nand a\t tab',
        u'quote_author': u'Stephen Ermshar',
        u'relationship_status': u'In engineering...',
        u'website': u'aswwu.com',
    }

# fields that should be visible regardless of the viewer's status
BASE_FIELDS = {
    "email",  # email is visible to not logged in users for individuals with privacy==0, but not for privacy==1, yikes..
    "full_name",
    "photo",
    "username",
    "views",
}

# fields that should only be visible to logged out users if the profile's privacy is "1"
IMPERSONAL_FIELDS = {
    'career_goals',
    'department',
    'favorite_books',
    'favorite_movies',
    'favorite_music',
    'gender',
    'graduate',
    'hobbies',
    'majors',
    'minors',
    'office',
    'office_hours',
    'personality',
    'pet_peeves',
    'preprofessional',
    'privacy',
    'quote',
    'quote_author',
    'relationship_status',
    'website',
}

# fields that should only be visible to logged in users
PERSONAL_FIELDS = {
    'attached_to',
    'birthday',
    'class_of',
    'class_standing',
    'high_school',
    'phone',
}

# fields that should only be visible to a profile's owner
SELF_FIELDS = {
    "wwuid",
    "favorite_food",  # change this, these regression tests are being written for current behavior, not desired
}


def build_profile_dict(user, update_dict, remove_keys, base_dict=BASE_PROFILE):
    """
    given a user, start with the BASE_PROFILE, or base_dict if provided, and construct a user object,
    adding or updating fields in update_dict, and removing fields listed in remove keys.
    :param user: a user for which to build the profile
    :param update_dict: a python dictionary of items to be added or updated
    :param remove_keys: a python set of string keys to be removed
    :param base_dict: (optional) an alternative base profile dictionary
    :return:
    """
    new_profile = dict()
    new_profile.update(base_dict)
    new_profile.update(user)
    new_profile.update(update_dict)
    remove_keys = remove_keys.intersection(set(new_profile.keys()))
    for remove_key in remove_keys:
        del new_profile[remove_key]
    return new_profile


def assert_update_profile(user, session, custom_fields={}):
    profile_fields = dict()
    profile_fields.update(BASE_PROFILE)
    profile_fields.update(user)
    profile_fields.update(custom_fields)
    update_response = mask_requests.post_update_profile(user["username"], profile_fields, session)
    assert update_response.status_code == 200
    assert json.loads(update_response.text) == "success"
    profile_response = mask_requests.get_profile(testing["current_year"], user["username"], session)
    assert profile_response.status_code == 200
    utils.assert_is_equal_sub_dict(profile_fields, json.loads(profile_response.text))


def test_update_profile(testing_server):
    users = utils.load_csv(USERS_PATH, use_unicode=True)
    for user in users:
        login_response_text, session = assert_verify_login(user)
        assert_update_profile(user, session)


def test_search_all(testing_server):
    users = utils.load_csv(USERS_PATH, use_unicode=True)
    expected_results = []
    for user in users:
        login_response_text, session = assert_verify_login(user)
        assert_update_profile(user, session)
        updated_user = dict()
        updated_user.update(user)
        updated_user.update({u"photo": BASE_PROFILE[u"photo"]})
        del(updated_user[u"wwuid"])
        expected_results.append(updated_user)
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
    viewee_session = assert_verify_login(viewee)[1]
    assert_update_profile(viewee, viewee_session, {"privacy": "0"})

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
    viewee_session = assert_verify_login(viewee)[1]
    assert_update_profile(viewee, viewee_session, {"privacy": "1"})

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
    viewee_session = assert_verify_login(viewee)[1]
    assert_update_profile(viewee, viewee_session)

    viewer_session = assert_verify_login(viewer)[1]

    profile_response = mask_requests.get_profile(testing["current_year"], viewee["username"], viewer_session)

    hidden_keys = SELF_FIELDS
    expected_profile = build_profile_dict(viewee, {}, hidden_keys)

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
    user_session = assert_verify_login(user)[1]
    assert_update_profile(user, user_session)

    profile_response = mask_requests.get_profile(testing["current_year"], user["username"], user_session)

    expected_profile = build_profile_dict(user, {}, set())
    actual_profile = json.loads(profile_response.text)

    assert profile_response.status_code == 200
    utils.assert_is_equal_sub_dict(expected_profile, actual_profile)
