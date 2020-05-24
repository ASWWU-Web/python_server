import json

from settings import environment
from tests import utils as utils

from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.jobs import jobs_requests, jobs_data
from tests.aswwu.behaviors.jobs.jobs_data import JOB_DATA_POST
import distutils.dir_util


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


def assert_upload_resume_success(session, resume_file_name, job_id):
    resume_location = environment["temporary_files"] + "/" + resume_file_name

    distutils.dir_util.create_tree(environment["resumes_location"], [resume_file_name])
    utils.touch(resume_location)

    files = {'file': open(resume_location, 'rb')}

    url = jobs_requests.URLS["resume_upload"]
    response = session.post(url, files=files, data={"jobID": job_id})

    assert response.status_code == 201
    assert response.json() == {"status": "Submitted"}
    return response
