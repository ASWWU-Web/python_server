from settings import environment
from tests import utils as utils

from tests.aswwu.behaviors.jobs import jobs_requests
import distutils.dir_util

from tests.aswwu.behaviors.jobs.jobs_requests import post_resume_upload


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

    file_content = resume_file_name + " contents"
    file_object = open(resume_location, 'w+')
    file_object.write(file_content)
    file_object.close()


    file = {'file': open(resume_location, "r")}

    response = post_resume_upload(file, job_id, session)

    file["file"].close()

    assert response.status_code == 201
    assert response.json() == {"status": "Submitted"}
    return response, file_content
