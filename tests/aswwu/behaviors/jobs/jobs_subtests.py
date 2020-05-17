import json

from tests.aswwu.behaviors.jobs import jobs_requests
from tests.aswwu.behaviors.jobs.jobs_data import JOB_DATA_POST


def assert_new_job_success(session, new_job_owner, new_job_data=None):
    new_job_data = JOB_DATA_POST if new_job_data is None else new_job_data

    response = jobs_requests.post_job_new(new_job_data, session)

    assert response.status_code == 201
    assert json.loads((response.text))["status"] == "submitted"

    return response