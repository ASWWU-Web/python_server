from tests.aswwu.data.users import USERS

JOB_OWNER = USERS[0]
APPLICANT = USERS[1]
APPLICANT_2 = USERS[2]

JOB_DATA_POST = {
        "job_name": "new job name",
        "job_description": "new job description",
        "visibility": "true",
        "department": "Web",
        "owner": JOB_OWNER["username"],
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
    "owner": JOB_OWNER["username"],
    "featured": False,
    "job_description": "new job description",
    "department": "Web",
    "image": "",
    "job_name": "new job name",
    "visibility": True,
    "jobID": 1,
}

JOB_DATA_GET_ONE = {
    "owner": JOB_OWNER["username"],
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

JOB_DATA_EDITED_POST = JOB_DATA_POST.copy()
JOB_DATA_EDITED_POST.update(
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
    "owner": JOB_OWNER["username"],
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

APP_DATA = {
    "jobID": "1",
    "username": APPLICANT["username"],
    "answers": '['
               '{"questionID": "1", "answer": "question 1 answer"},'
               '{"questionID": "2", "answer": "question 2 answer"},'
               '{"questionID": "3", "answer": "question 3 answer"}'
               ']'
}