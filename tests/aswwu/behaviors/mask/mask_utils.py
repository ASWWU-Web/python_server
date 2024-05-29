import json

from tests.aswwu.behaviors.mask import mask_requests
from tests.aswwu.behaviors.mask.mask_data import BASE_PROFILE


def build_profile_dict(user, update_dict=dict(), remove_keys=set(), base_dict=BASE_PROFILE):
    """
    given a user, start with the BASE_PROFILE, or base_dict if provided, and construct a user object,
    adding or updating fields in update_dict, and removing fields listed in remove keys.
    :param user: a user for which to build the profile
    :param update_dict: (optional) a python dictionary of items to be added or updated
    :param remove_keys: (optional) a python set of string keys to be removed
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


def assert_update_profile(user, session, profile_dict):
    update_response = mask_requests.post_update_profile(user["username"], profile_dict, session)
    assert update_response.status_code == 200
    assert json.loads(update_response.text) == "success"