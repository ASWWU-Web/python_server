import tornado.web
import logging
import requests
import json
import re
from alchemy.setup import *

logger = logging.getLogger("pyserver")


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
		return self.get_secure_cookie("wwuid")


class IndexHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		# wwuid = self.current_user
		wwuid = "adsf"
		self.write(wwuid)


class LoginHandler(BaseHandler):
	def get(self):
		self.write({'error': 'You must login to access that content'})

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
					self.set_secure_cookie("wwuid", str(o['wwuid']), expires_days=30)
					logger.info("LoginHandler: success")
					self.write(o)
				else:
					logger.info("LoginHandler: error")
					self.write({'error':'invalid login credentials'})
			except Exception as e:
				logger.error("LoginHandler exception: "+ str(e.message))
				self.write({'error':str(e.message)})
		else:
			logger.error("LoginHandler: invalid post parameters")
			self.write({'error':'invalid post parameters'})
