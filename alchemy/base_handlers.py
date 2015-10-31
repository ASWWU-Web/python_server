import tornado.web
import logging
import requests
import json
import datetime
from alchemy.models import *
from alchemy.setup import *

logger = logging.getLogger("aswwu")

def authenticate(func):
    def func_wrapper(*args, **kwargs):
        logger.debug(*args)
        current_user = '2000580'
        return func(*args, **kwargs)
    return func_wrapper

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        token = self.request.headers.get('token', None)
        user = None
        if token:
            h = token.split('|')
            t = query_by_id(Token,h[0])
            logger.debug(hashlib.sha512(str(t.wwuid)+str(t.auth_salt)).hexdigest())
            if t:
                if str(t.wwuid) == str(h[1]):
                    if str(hashlib.sha512(str(t.wwuid)+str(t.auth_salt)).hexdigest()) == str(h[2]):
                        user = query_user(t.wwuid)
        return user


class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        self.write(user.to_json())


class LoginHandler(BaseHandler):
    def get(self):
        self.write('<form method="post"><input name="username"><input name="password"><input type="submit"></form>')

    def post(self):
        logger.debug("'class':'LoginHandler','method':'post', 'message': 'invoked'")
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)

        if username and password:
            try:
                r = requests.post(self.application.options.auth_url, data = {'username': username, 'password': password}, verify=False)
                o = json.loads(r.text)
                if 'user' in o:
                    o = o['user']
                    user = query_by_wwuid(User,o['wwuid'])
                    if not user:
                        user = User(wwuid=o['wwuid'], username=o['username'], full_name=o['fullname'], status=o['status'])
                        addOrUpdate(user)
                    token = Token(wwuid=o['wwuid'])
                    addOrUpdate(token)
                    logger.debug(token)
                    self.write({'user': user.to_json(), 'token': str(token)})
                else:
                    logger.info("LoginHandler: error")
                    self.write({'error':'invalid login credentials'})
            except Exception as e:
                logger.error("LoginHandler exception: "+ str(e.message))
                self.write({'error': str(e.message)})
        else:
            logger.error("LoginHandler: invalid post parameters")
            self.write({'error':'invalid post parameters'})
