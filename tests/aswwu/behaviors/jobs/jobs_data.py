from tests import utils
from tests.aswwu.data.paths import USERS_PATH

DEFAULT_JOB_OWNER = utils.load_csv(USERS_PATH)[0]["username"]

DEFAULT_JOB_DATA_POST = {
        "job_name": "new job name",
        "job_description": "new job description",
        "visibility": "false",
        "department": "Web",
        "owner": DEFAULT_JOB_OWNER,
        "image": "",
        "featured": "true",
        # the questions argument needs to be one string,
        # because it's re-decoded from json in the server.
        "questions": '['
                     '{"question": "question 1"},'
                     '{"question": "question 2"},'
                     '{"question": "question 3"}'
                     ']'
    }

DEFAULT_JOB_DATA_GET_ALL = {
    "owner": DEFAULT_JOB_OWNER,
    "featured": True,
    "job_description": "new job description",
    "department": "Web",
    "image": "",
    "job_name": "new job name",
    "visibility": False,
    "jobID": 1,
}

DEFAULT_JOB_DATA_GET_ONE = {
    "owner": DEFAULT_JOB_OWNER,
    "featured": True,
    "job_description": "new job description",
    "department": "Web",
    "image": "",
    "job_name": "new job name",
    "visibility": False,
    "jobID": 1,
    "questions": [
        {"question": "question 1", "id": 1},
        {"question": "question 2", "id": 2},
        {"question": "question 3", "id": 3}
    ]
}
