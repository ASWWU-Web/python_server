# base_handlers.py

import tornado.web
import logging
import requests
import json
import time
import datetime
import hmac
import base64
import hashlib

# import modles and alchemy functions as needed
from aswwu.models import *
from aswwu.alchemy import *

logger = logging.getLogger("aswwu")

# model used only in this file
# acts as an extension of the User and Profile models
class LoggedInUser:
    def __init__(self, wwuid):
        self.wwuid = wwuid
        profile = query_by_wwuid(Profile, wwuid)
        user = query_user(wwuid)
        if len(profile) == 0:
            # TODO: This needs to be done better. (Should move entire profile except class_standing)
            old_profile = archive_s.query(globals()['Archive1516']).filter_by(wwuid=str(wwuid)).all()
            if (len(old_profile) == 1 and hasattr(old_profile[0], "photo")):
                new_profile = Profile(wwuid=str(wwuid), username=user.username, full_name=user.full_name, photo=old_profile[0].photo)
            else:
                new_profile = Profile(wwuid=str(wwuid), username=user.username, full_name=user.full_name)
            profile = addOrUpdate(new_profile)
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
        message = wwuid+"|"+str(now)
        return message+"|"+self.generateHMACDigest(message)

    # see if the authorization token received from the user has been tampered with (i.e. copied or stolen)
    def validateToken(self, token):
        token = token.split("|")
        if len(token) != 3:
            return false
        compareTo = self.generateHMACDigest(token[0]+"|"+token[1])
        return compareTo == token[2]

    # global hook that allows the @tornado.web.authenticated decorator to function
    # checks for an authorization header and attempts to validate the user with that information
    def get_current_user(self):
        authorization = self.request.headers.get('Authorization', None)

        try:
            token = authorization.split(" ")
            wwuid = token[1].split("|")[0]
            dateCreated = int(token[1].split("|")[1])
            now = int(time.mktime(datetime.datetime.now().timetuple()))
            # check if token is exactly 2 parts, starts with HMAC, was created with the last 2 weeks (14 days), and is a valid token
            if len(token) != 2 or token[0] != "HMAC" or (now - dateCreated) > (60*60*24*14) or not self.validateToken(token[1]):
                user = None
            else:
                user = LoggedInUser(wwuid)
        except Exception as e:
            user = None

        return user

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
        self.write({'error': 'not logged in'})

    # the main login/registration handler
    def post(self):
        logger.debug("'class':'LoginHandler','method':'post', 'message': 'invoked'")
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)

        # make sure we actually received something from the user
        if username and password:
            try:
                # expects a dictionary to be returned here (JSON)
                user_dict = self.loginWithWWU(username, password)
                if user_dict:
                    # lookup the user
                    user = query_user(user_dict['wwuid'])
                    if not user:
                        # if a matching user doesn't exist, create it
                        user = User(wwuid=user_dict['wwuid'], username=user_dict['username'], full_name=user_dict['fullname'], status=user_dict['status'])
                        addOrUpdate(user)
                    # generate a new token for this login
                    token = self.generateToken(user_dict['wwuid'])
                    # create a new LoggedInUser model
                    user = LoggedInUser(user_dict['wwuid'])
                    # this worked out, send it all back to the user
                    self.write({'user': user.to_json(), 'token': str(token)})
                else:
                    # self.loginWithWWU didn't return what we expected
                    logger.info("LoginHandler: Invalid Credentials")
                    self.write({'error':'YOU SHALL NOT PASS (Invalid login credentials)'})
            except Exception as e:
                # you've got some debugging to get through if you're here
                logger.error("LoginHandler exception: "+ str(e.message))
                self.write({'error': "Server Error: " + str(e.message)})
        else:
            # tell the user to send some better information
            logger.error("LoginHandler: invalid post parameters")
            self.write({'error':'invalid post parameters'})

# verify a user's authorization token
class BaseVerifyLoginHandler(BaseHandler):
    def get(self):
        # globally available parameter
        # is the returned result of get_current_user() above
        user = self.current_user
        if user:
            # if a user exists, refresh their token for them
            self.write({'user': user.to_json(), 'token': self.generateToken(user.wwuid)})
        else:
            self.set_status(401)
            self.write({'error': 'not logged in'})
