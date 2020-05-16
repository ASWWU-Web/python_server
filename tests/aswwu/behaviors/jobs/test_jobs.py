import tests.utils as utils
from tests.aswwu.behaviors.mask.mask_utils import build_profile_dict, assert_update_profile
from tests.aswwu.data.paths import USERS_PATH
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.auth.auth_requests import post_roles
from tests.aswwu.behaviors.jobs import jobs_requests
import json
import distutils.dir_util
from settings import environment
import settings


# "new": "job/new",
def test_new_job(testing_server):
    new_job_owner = utils.load_csv(USERS_PATH)[0]
    required_permissions = ["forms-admin"]

    session = assert_verify_login(new_job_owner)[1]
    post_roles(new_job_owner["wwuid"], required_permissions)

    new_job_data = {
        "job_name": "new job name",
        "job_description": "new job description",
        "visibility": "false",
        "department": "Web",
        "owner": new_job_owner["username"],
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

    response = jobs_requests.post_job_new(new_job_data, session)

    assert response.status_code == 201
    assert json.loads((response.text))["status"] == "submitted"


# "job_view": "job/view",
def test_job_view():
    pass


# "job_delete": "job/delete",
def test_job_delete():
    pass


# "job_edit": "job/edit",
def test_job_edit():
    pass


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
