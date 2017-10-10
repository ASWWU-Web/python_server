# base_handlers.py

import datetime
import hashlib
import hmac
import json
import logging
import time

import requests
import tornado.web

from settings import testing

# import models and alchemy functions as needed
import aswwu.models.mask as mask_model
import aswwu.alchemy as alchemy

logger = logging.getLogger("aswwu")

# model used only in this file
# acts as an extension of the User and Profile models
class LoggedInUser:
    def __init__(self, wwuid):
        self.wwuid = wwuid
        profile = alchemy.query_by_wwuid(mask_model.Profile, wwuid)
        user = alchemy.query_user(wwuid)
        if len(profile) == 0:
            old_profile = alchemy.archive_db.query(globals()['Archive' + get_last_year()]).filter_by(wwuid=str(wwuid)).all()
            new_profile = mask_model.Profile(wwuid=str(wwuid), username=user.username, full_name=user.full_name)
            if len(old_profile) == 1:
                self.import_profile(new_profile, old_profile[0].export_info())
            profile = alchemy.addOrUpdate(new_profile)
        else:
            profile = profile[0]
        self.username = user.username
        self.full_name = profile.full_name
        self.photo = profile.photo
        if user.roles:
            self.roles = user.roles.split(',')
        else:
            self.roles = []
        self.status = user.status

    def to_json(self):
        return {'wwuid': str(self.wwuid), 'username': str(self.username), 'full_name': str(self.full_name), 'photo': self.photo, 'roles': str(','.join(self.roles)), 'status': str(self.status)}

    def import_profile(self, profile, exported_json):
        for field in exported_json:
            if exported_json[field]:
                setattr(profile, field, exported_json[field])


# this is the root/base handler for all other handlers
class BaseHandler(tornado.web.RequestHandler):
    # newer JS frameworks send an OPTIONS request as a "preflight" to check if the server is safe
    # this just tells the framework that it is safe to send data here
    def options(self, *path_args, **path_kwargs):
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, token")
        pass

    # allow data to come from anywhere
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    # creates an HMAC digest that is a hexadecimal hash based on a provided message
    def generateHMACDigest(self, message):
        secret = self.application.settings['secret_key']
        signature = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
        return signature

    # create a authorization token for the given WWUID based on the current time
    def generateToken(self, wwuid):
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        message = str(wwuid)+"|"+str(now)
        return message+"|"+self.generateHMACDigest(message)

    # see if the authorization token received from the user has been tampered with (i.e. copied or stolen)
    def validateToken(self, token):
        token = token.split("|")
        if len(token) != 3:
            return False
        compareTo = self.generateHMACDigest(token[0]+"|"+token[1])
        return compareTo == token[2]

    # global hook that allows the @tornado.web.authenticated decorator to function
    # checks for an authorization header and attempts to validate the user with that information
    def get_current_user(self):
        if not testing['dev']:
            try:
                if not self.get_cookie("token"):
                    user = None
                    self.set_cookie('token', '', domain='.aswwu.com', expires_days=14)
                    logger.error("There was no cookie! You're not logged in!")
                else:
                    token = self.get_cookie("token")
                    wwuid = token.split("|")[0]
                    dateCreated = int(token.split("|")[1])
                    now = int(time.mktime(datetime.datetime.now().timetuple()))
                    # check if token was created with the last 2 weeks (14 days) and is a valid token
                    if (now - dateCreated) > (60 * 60 * 24 * 14) or not self.validateToken(token):
                        user = None
                    else:
                        user = LoggedInUser(wwuid)
            except Exception as e:
                user = None

            return user
        else:
            return LoggedInUser(testing['developer'])

    def prepare(self):
        # some modern JS frameworks force data to be sent as JSON
        # this isn't a bad thing at all, just requires us to "prepare" the data before it's used internally
        if "Content-Type" in self.request.headers and self.request.headers["Content-Type"].startswith("application/json") and len(self.request.arguments) == 0:
            try:
                json_data = json.loads(str(self.request.body))
                for key in json_data: json_data[key] = [json_data[key]]
                self.request.arguments = json_data
            except Exception as e:
                pass

# effectively useless, but at least provides an endpoint for people accessing "/" by accident
class BaseIndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        self.write(user.to_json())

# login and/or register users as needed
class BaseLoginHandler(BaseHandler):
    # verify login information with the WWU servers somehow
    def loginWithWWU(self, username, password):
        # NOTE: this url is old, yet still functional
        # expect it to change eventually
        mask_url = "https://www.wallawalla.edu/auth/mask.php"

        # pass the username and password to our accepted URL
        r = requests.post(mask_url, data = {'username': username, 'password': password}, verify=True)

        # parse out the ugly response
        parsedUser = r.text.encode('utf-8')[6:-7]
        parsedUser = json.loads(parsedUser)['user']
        if parsedUser:
            parsedUser['wwuid'] = parsedUser['wwcid']
            return parsedUser
        else:
            return None

    # if someone gets here they have bigger problems than not being logged in
    def get(self):
        logger.debug("not logged in")
        self.set_status(401)
        self.write({'error': 'not logged in'})

    # the main login/registration handler
    def post(self):
        logger.debug("'class':'LoginHandler','method':'post', 'message': 'invoked'")
        self.write({'error':'We\'ve switched over to the university login. Try refreshing the page and clearing your cache to login with the new method. If you\'re having more issues email aswwu.webmaster@wallawalla.edu'})

# verify a user's authorization token
class BaseVerifyLoginHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # globally available parameter
        # is the returned result of get_current_user() above
        user = self.current_user
        if user:
            # if a user exists, refresh their token for them
            token = self.generateToken(user.wwuid)
            self.write({'user': user.to_json(), 'token': token})
            self.set_cookie("token", token, domain='.aswwu.com', expires_days=14)
        else:
            self.set_status(401)
            self.write({'error': 'not logged in'})


def get_last_year():
    year = tornado.options.options.current_year
    return str(int(year[:2]) - 1) + str(int(year[2:4]) - 1)
