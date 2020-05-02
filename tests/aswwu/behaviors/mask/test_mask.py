import requests
from tests.conftest import testing_server
import tests.utils as utils
from tests.aswwu.data.paths import USERS_PATH
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.mask import mask_requests
import json
from settings import testing


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


def test_profile_handler(testing_server):
    users = utils.load_csv(USERS_PATH, use_unicode=True)
    for user in users:
        login_response_text, session = assert_verify_login(user)
        assert_update_profile(user, session)

    viewing_user = users[0]
    session = assert_verify_login(viewing_user)[1]
    for user in users:
        profile_response = mask_requests.get_profile(testing["current_year"], user["username"], session)
        expected_profile = dict()
        expected_profile.update(BASE_PROFILE)
        expected_profile.update(user)
        del(expected_profile[u"wwuid"])
        del(expected_profile[u"favorite_food"])
        actual_profile = json.loads(profile_response.text)
        assert profile_response.status_code == 200
        utils.assert_is_equal_sub_dict(expected_profile, actual_profile)
