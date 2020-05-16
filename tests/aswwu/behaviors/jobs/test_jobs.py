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
