import requests
from settings import keys, testing

BASE_URL = testing['base_url'] + ':' + str(testing['port'])
PROFILE_URL = '/'.join([BASE_URL, 'profiles'])
