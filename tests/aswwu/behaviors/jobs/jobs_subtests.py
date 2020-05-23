import json

from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.jobs import jobs_requests, jobs_data
from tests.aswwu.behaviors.jobs.jobs_data import JOB_DATA_POST


def assert_new_job_success(session, new_job_data):
    response = jobs_requests.post_job_new(new_job_data, session)

    assert response.status_code == 201
    assert response.json() == {"status": "submitted"}

    return response


def assert_new_app_success(session, new_app_data):
    response = jobs_requests.post_app_submit(new_app_data, session)

    assert response.status_code == 201
    assert response.json() == {"status": "submitted"}

    return response
