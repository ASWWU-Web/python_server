import tests.utils as utils
from tests.aswwu.behaviors.jobs.jobs_subtests import assert_new_job_success
from tests.aswwu.data.paths import USERS_PATH
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.auth.auth_requests import post_roles
from tests.aswwu.behaviors.jobs import jobs_data, jobs_requests
import json


# "new": "job/new",
def test_new_job(testing_server):
    new_job_owner = utils.load_csv(USERS_PATH)[0]
    required_permissions = ["forms-admin"]

    session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], required_permissions)

    assert_new_job_success(session, new_job_owner)


# "job_view": "job/view",
def test_job_view(testing_server):
    new_job_owner = utils.load_csv(USERS_PATH)[0]
    create_job_permissions = ["forms-admin"]

    session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], create_job_permissions)

    assert_new_job_success(session, new_job_owner)

    job_view_all_response = jobs_requests.get_job_view()
    expected_job_view_all_response = jobs_data.JOB_DATA_GET_ALL
    actual_job_view_all_response = json.loads(job_view_all_response.text)["forms"][0]
    assert job_view_all_response.status_code == 200
    assert actual_job_view_all_response == expected_job_view_all_response

    job_view_one_response = jobs_requests.get_job_view(1)
    expected_job_view_one_response = jobs_data.JOB_DATA_GET_ONE
    actual_job_view_one_response = json.loads(job_view_one_response.text)["form"]
    assert job_view_one_response.status_code == 200
    assert actual_job_view_one_response == expected_job_view_one_response


# "job_delete": "job/delete",
def test_job_delete():
    pass


# "job_edit": "job/edit",
def test_job_edit(testing_server):
    new_job_owner = utils.load_csv(USERS_PATH)[0]
    required_permissions = ["forms-admin"]

    session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], required_permissions)

    assert_new_job_success(session, new_job_owner)

    job_edit_response = jobs_requests.post_job_edit(1, jobs_data.JOB_DATA_EDIT_POST, session)
    actual_job_edit_response = json.loads(job_edit_response.text)
    assert job_edit_response.status_code == 200
    assert actual_job_edit_response["status"] == "Form Updated"

    job_view_one_response = jobs_requests.get_job_view(1)
    expected_job_view_one_response = jobs_data.JOB_DATA_GET_EDITED_ONE
    actual_job_view_one_response = json.loads(job_view_one_response.text)["form"]
    assert job_view_one_response.status_code == 200
    assert actual_job_view_one_response == expected_job_view_one_response


# "app_submit": "application/submit",
def test_app_submit():
    pass


# "app_view": "application/view",
def test_app_view():
    pass


# "app_status": "application/status",
def test_app_view():
    pass


# "app_export": "application/export",
def test_app_export():
    pass


# "resume_upload": "resume/upload",
def test_resume_upload():
    pass


# "resume_download": "resume/download",
def test_resume_download():
    pass
