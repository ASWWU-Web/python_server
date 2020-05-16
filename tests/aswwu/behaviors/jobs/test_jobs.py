from tests.aswwu.behaviors.mask.mask_data import BASE_PROFILE, IMPERSONAL_FIELDS, PERSONAL_FIELDS, SELF_FIELDS, DEFAULT_MASK_PHOTO
import tests.utils as utils
from tests.aswwu.behaviors.mask.mask_utils import build_profile_dict, assert_update_profile
from tests.aswwu.data.paths import USERS_PATH
from tests.aswwu.behaviors.auth.auth_subtests import assert_verify_login
from tests.aswwu.behaviors.jobs import jobs_requests
import json
import distutils.dir_util
from settings import environment
import settings

CURRENT_YEAR = settings.environment["current_year"]


# "new": "job/new",
def test_new_job():
    pass


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
