import os

keys = {
    'hmac': bytes(os.getenv('HMAC_KEY', 'dev'), encoding='utf8'),
    'samlEndpointKey': os.getenv('SAML_KEY', 'dev')
}
testing = {
    'dev': False if os.getenv('PROD', 'false') == 'true' else True,
    'developer': os.getenv('WWUID')
}
email = {
    'username': os.getenv('EMAIL_USER'),
    'password': os.getenv('EMAIL_PASSWORD')
}
