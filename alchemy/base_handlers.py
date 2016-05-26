import tornado.web
import logging
import requests
import json
import time
import datetime
from alchemy.models import *
from alchemy.setup import *
import hmac
import base64
import hashlib

logger = logging.getLogger("aswwu")

class LoggedInUser:
    def __init__(self, wwuid):
        self.wwuid = wwuid
        profile = query_by_wwuid(Profile, wwuid)
        user = query_user(wwuid)
        if len(profile) == 0:
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


class BaseHandler(tornado.web.RequestHandler):
    def options(self, *path_args, **path_kwargs):
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, token")
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def generateHMACDigest(self, message):
        secret = self.application.settings['secret_key']
        signature = hmac.new(secret, message, digestmod=hashlib.sha256).hexdigest()
        return signature

    def generateToken(self, wwuid):
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        message = wwuid+"|"+str(now)
        return message+"|"+self.generateHMACDigest(message)

    def validateToken(self, token):
        token = token.split("|")
        if len(token) != 3:
            return false
        compareTo = self.generateHMACDigest(token[0]+"|"+token[1])
        return compareTo == token[2]

    def get_current_user(self):
        authorization = self.request.headers.get('Authorization', None)
        token = authorization.split(" ")

        try:
            wwuid = token[1].split("|")[0]
            dateCreated = int(token[1].split("|")[1])
            now = int(time.mktime(datetime.datetime.now().timetuple()))
            if len(token) != 2 or token[0] != "HMAC" or (now - dateCreated) > (60*60*24*14) or not self.validateToken(token[1]):
                user = None
            else:
                user = LoggedInUser(wwuid)
        except Exception as e:
            user = None

        return user

    def prepare(self):
        if "Content-Type" in self.request.headers and self.request.headers["Content-Type"].startswith("application/json") and len(self.request.arguments) == 0:
            try:
                json_data = json.loads(self.request.body)
                self.request.arguments = json_data
            except Exception as e:
                pass


class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        self.write(user.to_json())


class LoginHandler(BaseHandler):
    def get(self):
        logger.debug("not logged in")
        self.write({'error': 'not logged in'})

    def post(self):
        logger.debug("'class':'LoginHandler','method':'post', 'message': 'invoked'")
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        withFire = self.get_argument('withFire', False)

        if username and password:
            try:
                r = requests.post(self.application.options.auth_url, data = {'username': username, 'password': password}, verify=False)
                o = json.loads(r.text)
                if 'user' in o:
                    o = o['user']
                    user = query_user(o['wwuid'])
                    if not user:
                        user = User(wwuid=o['wwuid'], username=o['username'], full_name=o['full_name'], status=o['status'])
                        addOrUpdate(user)
                    if withFire:
                        from firebase_token_generator import create_token
                        auth_payload = user.to_json()
                        auth_payload['uid'] = user.wwuid;
                        token = create_token("peP0kwjeCWvjslEBN1gFQk38Y0UqaivhHGdnFPSO", auth_payload)
                    else:
                        token = self.generateToken(o['wwuid'])
                    user = LoggedInUser(o['wwuid'])
                    self.write({'user': user.to_json(), 'token': str(token)})
                else:
                    logger.info("LoginHandler: error"+r.text)
                    self.write({'error':'invalid login credentials'})
            except Exception as e:
                logger.error("LoginHandler exception: "+ str(e.message))
                self.write({'error': str(e.message)})
        else:
            logger.error("LoginHandler: invalid post parameters")
            self.write({'error':'invalid post parameters'})


class VerifyLoginHandler(BaseHandler):
    def get(self):
        user = self.current_user
        if user:
            self.write({'user': user.to_json(), 'token': self.generateToken(user.wwuid)})
        else:
            self.set_status(401)
            self.write({'error': 'not logged in'})
