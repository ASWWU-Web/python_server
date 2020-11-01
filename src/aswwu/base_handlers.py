# base_handlers.py

from builtins import str
from builtins import object
import datetime
import hashlib
import hmac
import json
import logging
import time

import tornado.web

from settings import keys, environment

# import models and alchemy functions as needed
import src.aswwu.models.mask as mask_model
import src.aswwu.alchemy_new.mask as mask
import src.aswwu.alchemy_new.archive as archive
import src.aswwu.archive_models as archives
import src.aswwu.exceptions as exceptions

logger = logging.getLogger(environment["log_name"])


# model used only in this file
# acts as an extension of the User and Profile models
def import_profile(profile, exported_json):
    for field in exported_json:
        if exported_json[field]:
            setattr(profile, field, exported_json[field])


class LoggedInUser(object):
    def __init__(self, wwuid):
        self.wwuid = wwuid
        profile = mask.query_by_wwuid(mask_model.Profile, wwuid)
        user = mask.query_user(wwuid)
        if len(profile) == 0:
            old_profile = archive.archive_db.query(archives.get_archive_model(get_last_year())).\
                filter_by(wwuid=str(wwuid)).all()
            new_profile = mask_model.Profile(wwuid=str(wwuid), username=user.username, full_name=user.full_name)
            if len(old_profile) == 1:
                import_profile(new_profile, old_profile[0].export_info())
            profile = mask.add_or_update(new_profile)
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
        return {'wwuid': str(self.wwuid), 'username': self.username, 'full_name': self.full_name,
                'photo': self.photo, 'roles': ','.join(self.roles), 'status': self.status}


# this is the root/base handler for all other handlers
class BaseHandler(tornado.web.RequestHandler):
    # newer JS frameworks send an OPTIONS request as a "preflight" to check if the server is safe
    # this just tells the framework that it is safe to send data here
    def options(self, *path_args, **path_kwargs):
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, token")
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')

    # allow data to come from anywhere
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    # creates an HMAC digest that is a hexadecimal hash based on a provided message
    def generate_hmac_digest(self, message):
        secret = self.application.settings['secret_key']
        signature = hmac.new(str.encode(secret), str.encode(message), digestmod=hashlib.sha256).hexdigest()
        return signature

    # create a authorization token for the given WWUID based on the current time
    def generate_token(self, wwuid):
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        message = str(wwuid)+"|"+str(now)
        return message+"|"+self.generate_hmac_digest(message)

    # see if the authorization token received from the user has been tampered with (i.e. copied or stolen)
    def validate_token(self, token):
        token = token.split("|")
        if len(token) != 3:
            return False
        compare_to = self.generate_hmac_digest(token[0] + "|" + token[1])
        return compare_to == token[2]

    # global hook that allows the @tornado.web.authenticated decorator to function
    # checks for an authorization header and attempts to validate the user with that information
    def get_current_user(self):
        if not environment['dev']:
            try:
                if not self.get_cookie("token"):
                    user = None
                    self.set_cookie('token', '', domain='.aswwu.com', expires_days=14)
                    logger.error("There was no cookie! You're not logged in!")
                else:
                    token = self.get_cookie("token")
                    wwuid = token.split("|")[0]
                    date_created = int(token.split("|")[1])
                    now = int(time.mktime(datetime.datetime.now().timetuple()))
                    # check if token was created with the last 2 weeks (14 days) and is a valid token
                    if (now - date_created) > (60 * 60 * 24 * 14) or not self.validate_token(token):
                        user = None
                    else:
                        user = LoggedInUser(wwuid)
            except:
                user = None

            return user
        else:
            return LoggedInUser(environment['developer'])

    def prepare(self):
        # some modern JS frameworks force data to be sent as JSON
        # this isn't a bad thing at all, just requires us to "prepare" the data before it's used internally
        if "Content-Type" in self.request.headers and self.request.headers["Content-Type"].\
                startswith("application/json") and len(self.request.arguments) == 0:
            try:
                json_data = json.loads(str(self.request.body))
                for key in json_data:
                    json_data[key] = [json_data[key]]
                self.request.arguments = json_data
            except:
                pass

    def write_error(self, status_code, **kwargs):
        self.write({'status': str(kwargs['exc_info'][1])})
        if status_code >= 500:
            logger.error("{} error".format(self.__class__.__name__))

    def get_argument(self, query, default=None):
        result = super().get_argument(query, default)
        if not result:
            return json.loads(self.request.body).get(query, default)
        return result

class BaseLoginHandler(BaseHandler):
    def get(self):
        self.set_status(401)
        self.write({'error': 'not logged in'})

    def post(self):
        self.set_status(500)
        self.write({'error': 'not implemented'})


# verify a user's authorization token
class BaseVerifyLoginHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        """
        The verify endpoint for the front-end. This endpoint
        will update the user's cookie and send them info back
        about their account.
        """
        # get the users info
        user = self.current_user
        # check if the user is logged in
        if not user:
            self.set_status(401)
            self.write({'error': 'not logged in'})
            return
        # if a user exists, refresh their token for them
        token = self.generate_token(user.wwuid)
        self.write({
            'user': user.to_json(),
            'token': token
        })
        # set the cookie header in the response
        self.set_cookie("token", token, domain='.aswwu.com', expires_days=14)

    def post(self):
        """
        The verify endpoint for SAML only. This endpoint will
        get or create a user's account info and send it back
        to the SAML container. It also sets the cookie which
        will login the user on the front-end.
        """
        # check secret key to ensure this is the SAML conatiner
        secret_key = self.get_argument('secret_key', None)
        if secret_key != keys["samlEndpointKey"]:
            logger.info("Unauthorized Access Attempted")
            self.write({'error': 'Unauthorized Access Attempted'})
            return
        # get the SAML data from the request
        employee_id = self.get_argument('employee_id', None)
        full_name = self.get_argument('full_name', None)
        email_address = self.get_argument('email_address', None)
        # check that the data was given in the request
        if None in (employee_id, full_name, email_address):
            logger.info("AccountHandler: error")
            self.write({'error': 'invalid parameters'})
            return
        # get the user from the database
        user = mask.query_user(employee_id)
        # create a new user if necessary
        if not user:
            user = mask_model.User(wwuid=employee_id,
                                   username=email_address.split('@', 1)[0],
                                   full_name=full_name,
                                   status='Student')
            mask.add_or_update(user)
            # initial view for the new user
            add_null_view('null.user', user.username)
        # return the new users token and information
        token = self.generate_token(user.wwuid)
        self.write({
            'user': user.to_json(),
            'token': token
        })
        # set the cookie header in the response
        self.set_cookie("token", token, domain='.aswwu.com', expires_days=14)


class RoleHandler(BaseHandler):
    def post(self, wwuid):
        """
        Modify roles in the users table, accessible only in a testing environment.
        Writes the modified user object.
        """
        if not environment['pytest']:
            raise exceptions.Forbidden403Exception('Method Forbidden')
        else:
            user = mask.query_user(wwuid)
            if user == list():
                exceptions.NotFound404Exception('user with specified wwuid not found')
            else:
                body = self.request.body.decode('utf-8')
                body_json = json.loads(body)
                user.roles = ','.join(body_json['roles'])
                mask.add_or_update(user)
                self.set_status(201)
                self.write({'user': user.to_json()})


def get_last_year():
    year = tornado.options.options.current_year
    return str(int(year[:2]) - 1) + str(int(year[2:4]) - 1)


def add_null_view(user, profile):
    views = mask.people_db.query(mask_model.ProfileView)\
        .filter_by(viewer=user, viewed=profile).all()
    if len(views) == 0:
        view = mask_model.ProfileView()
        view.viewer = user
        view.viewed = profile
        view.last_viewed = datetime.datetime.now()
        view.num_views = 0
        mask.add_or_update(view)
