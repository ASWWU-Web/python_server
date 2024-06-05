from tests.aswwu.behaviors.jobs.jobs_requests import get_resume_download
from tests.aswwu.behaviors.jobs.jobs_subtests import assert_new_job_success, assert_new_app_success, \
    assert_upload_resume_success
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.auth.auth_requests import post_roles
from tests.aswwu.behaviors.jobs import jobs_data, jobs_requests
import json
import datetime
import pytest

pytestmark = pytest.mark.xfail

# "new": "job/new",
def test_new_job(testing_server):
    new_job_owner = jobs_data.JOB_OWNER
    required_permissions = ["forms-admin"]

    session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], required_permissions)

    assert_new_job_success(session, jobs_data.JOB_DATA_POST)


# "job_view": "job/view",
def test_job_view(testing_server):
    new_job_owner = jobs_data.JOB_OWNER
    create_job_permissions = ["forms-admin"]

    session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], create_job_permissions)

    assert_new_job_success(session, jobs_data.JOB_DATA_POST)

    # view many jobs
    job_view_all_response = jobs_requests.get_job_view()
    expected_job_view_all_response = jobs_data.JOB_DATA_GET_ALL
    actual_job_view_all_response = json.loads(job_view_all_response.text)["forms"][0]
    assert job_view_all_response.status_code == 200
    assert actual_job_view_all_response == expected_job_view_all_response

    # view a single job
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
    new_job_owner = jobs_data.JOB_OWNER
    required_permissions = ["forms-admin"]

    session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], required_permissions)

    assert_new_job_success(session, jobs_data.JOB_DATA_POST)

    # edit existing job
    job_edit_response = jobs_requests.post_job_edit(1, jobs_data.JOB_DATA_EDITED_POST, session)
    assert job_edit_response.status_code == 200
    assert job_edit_response.json() == {"status": "Form Updated"}

    # view newly edited job
    job_view_one_response = jobs_requests.get_job_view(1)
    expected_job_view_one_response = jobs_data.JOB_DATA_GET_EDITED_ONE
    assert job_view_one_response.status_code == 200
    assert job_view_one_response.json() == {"form": expected_job_view_one_response}


# "app_submit": "application/submit",
def test_app_submit(testing_server):
    new_job_owner, applicant = jobs_data.JOB_OWNER, jobs_data.APPLICANT
    create_job_permissions = ["forms-admin"]
    session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], create_job_permissions)
    assert_new_job_success(session, jobs_data.JOB_DATA_POST)

    applicant_session = assert_verify_login(applicant)[1]
    assert_new_app_success(applicant_session, jobs_data.APP_DATA)


# "app_view": "application/view",
def test_app_view_many(testing_server):
    new_job_owner, applicant = jobs_data.JOB_OWNER, jobs_data.APPLICANT
    create_job_permissions = ["forms-admin"]
    owner_session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], create_job_permissions)
    assert_new_job_success(owner_session, jobs_data.JOB_DATA_POST)

    # submit new application
    datetime_before_submission = datetime.datetime.now()
    applicant_session = assert_verify_login(applicant)[1]
    assert_new_app_success(applicant_session, jobs_data.APP_DATA)
    datetime_after_submission = datetime.datetime.now()

    JOB_ID = "1"
    date_format = '%Y-%m-%dT%H:%M:%S.%f'

    # view all applications for all users and all jobs
    app_view_all_response = jobs_requests.get_app_view(session=owner_session)
    assert app_view_all_response.status_code == 200
    assert app_view_all_response.json()["applications"][0]["username"] == applicant["username"]
    assert app_view_all_response.json()["applications"][0]["status"] == "new"
    assert app_view_all_response.json()["applications"][0]["jobID"] == JOB_ID
    updated_at_datetime = datetime.datetime.strptime(app_view_all_response.json()["applications"][0]["updated_at"], date_format)
    assert datetime_before_submission <= updated_at_datetime <= datetime_after_submission

    # view all applications for all jobs and one user
    app_view_all_user_response = jobs_requests.get_app_view(username=applicant["username"], session=owner_session)
    assert app_view_all_user_response.status_code == 200
    assert app_view_all_user_response.json()["applications"][0]["username"] == applicant["username"]
    assert app_view_all_user_response.json()["applications"][0]["status"] == "new"
    assert app_view_all_user_response.json()["applications"][0]["jobID"] == JOB_ID
    updated_at_datetime = datetime.datetime.strptime(app_view_all_user_response.json()["applications"][0]["updated_at"], date_format)
    assert datetime_before_submission <= updated_at_datetime <= datetime_after_submission

    # view all applications for all users and one job
    app_view_all_job_response = jobs_requests.get_app_view(job_id=JOB_ID, session=owner_session)
    assert app_view_all_job_response.status_code == 200
    assert app_view_all_job_response.json()["applications"][0]["username"] == applicant["username"]
    assert app_view_all_job_response.json()["applications"][0]["status"] == "new"
    assert app_view_all_job_response.json()["applications"][0]["jobID"] == JOB_ID
    updated_at_datetime = datetime.datetime.strptime(app_view_all_job_response.json()["applications"][0]["updated_at"], date_format)
    assert datetime_before_submission <= updated_at_datetime <= datetime_after_submission


# "app_view": "application/view",
def test_app_view_one(testing_server):
    new_job_owner, applicant = jobs_data.JOB_OWNER, jobs_data.APPLICANT
    create_job_permissions = ["forms-admin"]
    owner_session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], create_job_permissions)
    assert_new_job_success(owner_session, jobs_data.JOB_DATA_POST)

    # submit new application
    applicant_session = assert_verify_login(applicant)[1]
    assert_new_app_success(applicant_session, jobs_data.APP_DATA)

    JOB_ID = "1"

    # view an application for one user and one job
    app_view_one_response = jobs_requests.get_app_view(job_id=JOB_ID, username=applicant["username"], session=owner_session)
    assert app_view_one_response.status_code == 200
    assert app_view_one_response.json()["application"]["username"] == applicant["username"]
    assert app_view_one_response.json()["application"]["status"] == "new"
    assert app_view_one_response.json()["application"]["jobID"] == JOB_ID
    assert app_view_one_response.json()["application"]["answers"] == json.loads(jobs_data.APP_DATA["answers"])
    assert True



# "app_status": "application/status",
def test_app_status():
    pass


# "app_export": "application/export",
def test_app_export():
    pass


# "resume_upload": "resume/upload",
def test_resume_upload(testing_server):
    new_job_owner, applicant = jobs_data.JOB_OWNER, jobs_data.APPLICANT
    create_job_permissions = ["forms-admin"]
    owner_session = assert_verify_login(new_job_owner)[1]
    applicant_session = assert_verify_login(applicant)[1]
    post_roles(new_job_owner["wwuid"], create_job_permissions)
    assert_new_job_success(owner_session, jobs_data.JOB_DATA_POST)

    resume_file_name = "demo_resume.pdf"
    job_id = 1

    assert_upload_resume_success(applicant_session, resume_file_name, job_id)


# "resume_download": "resume/download",
def test_resume_download(testing_server):
    new_job_owner, applicant = jobs_data.JOB_OWNER, jobs_data.APPLICANT
    create_job_permissions = ["forms-admin"]
    owner_session = assert_verify_login(new_job_owner)[1]
    applicant_session = assert_verify_login(applicant)[1]
    post_roles(new_job_owner["wwuid"], create_job_permissions)
    assert_new_job_success(owner_session, jobs_data.JOB_DATA_POST)

    resume_file_name = "demo_resume.pdf"
    job_id = "1"

    expected_file_content = assert_upload_resume_success(applicant_session, resume_file_name, job_id)[1]
    response = get_resume_download(job_id, applicant["username"], owner_session)

    assert response.status_code == 200
    assert response.content == expected_file_content


