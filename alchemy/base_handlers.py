import tornado.web
import logging
import requests
import json
import datetime
from alchemy.models import *
from alchemy.setup import *

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
    def options(self):
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With")
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def get_current_user(self):
        token = self.request.headers.get('token', None)
        if not token:
            token = self.get_argument('token', None)
        user = None
        if token:
            h = token.split('|')
            t = query_by_id(Token,h[0])
            if t:
                if str(t.wwuid) == str(h[1]):
                    if str(hashlib.sha512(str(t.wwuid)+str(t.auth_salt)).hexdigest()) == str(h[2]):
                        now = datetime.datetime.now()
                        if (now - t.auth_time).seconds/60/60/24 <= 14: # 14 day
                            t.auth_time = now
                            addOrUpdate(t)
                            user = LoggedInUser(t.wwuid)
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
            print username, password
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
                        token = Token(wwuid=o['wwuid'])
                    addOrUpdate(token)
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
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        self.write(user.to_json())
