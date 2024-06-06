import requests
import settings

BASE_URL = settings.environment['base_url'] + ':' + str(settings.environment['port'])
URLS = {
    "profile": "profile",
    "search_fast": "search/names",
    "search_all": "search/all",
    "search": "search",
    "list_photos": "update/list_photos",
    "update": "update",
}
URLS = {key : BASE_URL + "/" + URLS[key] for key in URLS.keys()}


def get_profile(year, username, session=None):
    """
    (r"/profile/(.*)/(.*)", mask.ProfileHandler)
    :param year: the school year from which to query the student (i.e. '1718', '1819', '1920', etc.)
    :param username: the case-sensitive username of the test user whose profile is being queried
    :return:
    """
    session = requests.Session() if session is None else session

    request_url = URLS["profile"] + "/" + year + "/" + username
    resp = session.get(request_url)
    return resp


def get_search_names_fast(name_query, session=None):
    """
    (r"/search/names", mask.SearchNamesFast)
    :param name_query: a string to query full_name with
    :param session: optional, an authenticated session if available.
    :return:
    """
    session = requests.Session() if session is None else session

    request_url = URLS["search_fast"] + "?full_name=" + name_query
    resp = session.get(request_url)
    return resp


def get_search_all(session=None):
    """
    (r"/search/all", mask.SearchAllHandler)
    :param session: optional, an authenticated session if available.
    :return:
    """
    session = requests.Session() if session is None else session

    request_url = URLS["search_all"]
    resp = session.get(request_url)
    return resp


def get_profile_search(year, session=None, string_query=None, dictionary_query=None):
    """
    (r"/search/(.*)/(.*)", mask.SearchHandler)
    :param year: the school year from which to query the students (i.e. '1718', '1819', '1920', etc.)
    :param session: optional, an authenticated session if available.
    :param string_query: a custom string to query with (usually just a name in the normal search bar) ignores kwargs
    :param kwargs: if no string_query, build a query from a dictionary ({"full_name": "smith"}
    :return:
    """
    session = requests.Session() if session is None else session

    if string_query is not None:
        query = string_query
    elif dictionary_query is not None:
        query = ";".join([key + "=" + value for key, value in dictionary_query.items()])
    else:
        assert False  # you must provide a string query or a dictionary query
    request_url = URLS["search"] + "/" + year + "/" + query
    resp = session.get(request_url)
    return resp


def get_list_profile_photos(session=None):
    """
    (r"/update/list_photos", mask.ListProfilePhotoHandler)
    :param session: optional, an authenticated session if available, indicates which user's photos to list
    :return: the request response object
    """
    session = requests.Session() if session is None else session

    request_url = URLS["list_photos"]
    resp = session.get(request_url)
    return resp


def post_update_profile(username, profile_data, session=None):
    """
    (r"/update/(.*)", mask.ProfileUpdateHandler)
    :param username: the case-sensitive username of the test user whose profile is being updated
    :param session: optional, an authenticated session if available.
    :param profile_data: a dictionary containing mask fields (i.e. "full_name", "photo", "gender", "birthday", "email", etc.)
    :return: the request response object
    """
    session = requests.Session() if session is None else session

    request_url = URLS["update"] + "/" + username
    resp = session.post(request_url, json=profile_data)
    return resp
