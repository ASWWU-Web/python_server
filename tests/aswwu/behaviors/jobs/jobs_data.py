from tests import utils
from tests.aswwu.data.paths import USERS_PATH

# TODO: (stephen) set these consts to the whole user object and
#                 import to test file, rather than useing load_csv
#                 there. Refactor mask similarly. Also, create
#                 users dictionary in place of csv.
JOB_OWNER = utils.load_csv(USERS_PATH)[0]["username"]
APPLICANT = utils.load_csv(USERS_PATH)[1]["username"]

JOB_DATA_POST = {
        "job_name": "new job name",
        "job_description": "new job description",
        "visibility": "true",
        "department": "Web",
        "owner": JOB_OWNER,
        "image": "",
        "featured": "false",
        # the questions argument needs to be one string,
        # because it's re-decoded from json in the server.
        "questions": '['
                     '{"question": "question 1"},'
                     '{"question": "question 2"},'
                     '{"question": "question 3"}'
                     ']'
    }

JOB_DATA_GET_ALL = {
    "owner": JOB_OWNER,
    "featured": False,
    "job_description": "new job description",
    "department": "Web",
    "image": "",
    "job_name": "new job name",
    "visibility": True,
    "jobID": 1,
}

JOB_DATA_GET_ONE = {
    "owner": JOB_OWNER,
    "featured": False,
    "job_description": "new job description",
    "department": "Web",
    "image": "",
    "job_name": "new job name",
    "visibility": True,
    "jobID": 1,
    "questions": [
        {"question": "question 1", "id": 1},
        {"question": "question 2", "id": 2},
        {"question": "question 3", "id": 3}
    ]
}

JOB_DATA_EDIT_POST = JOB_DATA_POST.copy()
JOB_DATA_EDIT_POST.update(
    {
        "questions": '['
                     '{"question": "question 1 edited", "id": 1},'
                     '{"question": "question 2 edited", "id": 2},'
                     '{"question": "question 3 edited", "id": 3}'
                     ']',
        "visibility": "true",
        "featured": "true",
    }
)

JOB_DATA_GET_EDITED_ONE = {
    "owner": JOB_OWNER,
    "featured": True,
    "job_description": "new job description",
    "department": "Web",
    "image": "",
    "job_name": "new job name",
    "visibility": True,
    "jobID": 1,
    "questions": [
        {"question": "question 1 edited", "id": 1},
        {"question": "question 2 edited", "id": 2},
        {"question": "question 3 edited", "id": 3}
    ]
}

APP_DATA_POST = {
    "jobID": "1",
    "username": APPLICANT,
    "answers": '['
               '{"questionID": 1, "answer": "question 1 answer"},'
               '{"questionID": 2, "answer": "question 2 answer"},'
               '{"questionID": 3, "answer": "question 3 answer"}'
               ']'
}