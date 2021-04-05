keys = {
    'hmac':"fakekeystring",
    'samlEndpointKey': "fakekeystring"
}

email = {
    'username': 'aswwu.webmaster@wallawalla.edu',
    'password': 'fakepassword'
}

# this environment will bypass authentication and login `developer`
local_dev_environment = {
    'environment_name': 'Local Development',
    'pytest': False,
    'dev': True,
    'developer': 2029909,
    'port': 8888,
    'log_name': 'local_aswwu',
    'current_year': '1920',
    'databases_location': '../databases',
    'profile_photos_location': '../media/profiles',
    'resumes_location': '../databases/resume',
    'media_location': '../media',
    'pending_profile_photos_location': '../media/pending_profiles',
    'dismayed_profile_photos_location': '../media/dismayed_profiles'
}

pytest_environment = {
    'environment_name': 'Pytest Automated Testing',
    'pytest': True,
    'dev': False,
    'base_url': 'http://127.0.0.1',
    'port': 8888,
    'log_name': 'aswwu_test',
    'current_year': '1920',
    'original_testing_databases': './testing_databases',
    'temporary_files': './tmp',
    'databases_location': './tmp/databases',
    'profile_photos_location': './tmp/profile_photos',
    'resumes_location': './tmp/resume',
    'media_location': './tmp/media',
    'pending_profile_photos_location': './tmp/pending_profiles',
    'dismayed_profile_photos_location': './tmp/dismayed_profiles'
}

production_environment = {
    'environment_name': 'Production and Deployment',
    'pytest': False,
    'dev': False,
    'port': 8888,
    'log_name': 'aswwu',
    'current_year': '1920',
    'databases_location': '../databases',
    'profile_photos_location': '../media/profiles',  # TODO: (stephen) implement
    'resumes_location': '../databases/resume',  # TODO: (stephen) implement
    'media_location': '../media',
    'pending_profile_photos_location': '../media/pending_profiles',
    'dismayed_profile_photos_location': '../media/dismayed_profiles'
}

environment = pytest_environment
