keys = {
    'hmac':"fakekeystring",
    'samlEndpointKey': "fakekeystring"
}
testing = {
    'pytest': True,  # enables access to roles endpoint, set to false in production
    'dev': False,  # bypasses authentication and logs in `developer`
    'developer': 0000000,
    'base_url': 'http://127.0.0.1',
    'port': 8888,
    'log_name': 'aswwu_test',
    'current_year': '1920',
    'database': './testing_databases',
}
production = {
    'port': 8888,
    'log_name': 'aswwu',
    'current_year': '1920',
}
email = {
    'username': 'aswwu.webmaster@wallawalla.edu',
    'password': 'fakepassword'
}
database = {
    'location': './testing_databases'
}
