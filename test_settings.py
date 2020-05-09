keys = {
    'hmac':"fakekeystring",
    'samlEndpointKey': "fakekeystring"
}

email = {
    'username': 'aswwu.webmaster@wallawalla.edu',
    'password': 'fakepassword'
}

# bypasses authentication and login `developer`
local_dev_environment = {
    'environment_name': 'Local Development',
    'pytest': False,
    'dev': True,
    'developer': 2029909,
    'port': 8888,
    'log_name': 'local_aswwu',
    'current_year': '1920',
    'databases_location': '../databases',
}

pytest_environment = {
    'environment_name': 'Pytest Automated Testing',
    'pytest': True,
    'dev': False,
    'base_url': 'http://127.0.0.1',
    'port': 8888,
    'log_name': 'aswwu_test',
    'current_year': '1920',
    'testing_databases_location': './testing_databases',
    'databases_location': './testing_databases/temp_dbs',
}

production_environment = {
    'environment_name': 'Production and Deployment',
    'pytest': False,
    'dev': False,
    'port': 8888,
    'log_name': 'aswwu',
    'current_year': '1920',
    'databases_location': '../databases',
}

environment = pytest_environment
