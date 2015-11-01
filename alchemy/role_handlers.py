import tornado.web
import logging
import requests
import json
import datetime
from sqlalchemy import or_
from alchemy.models import *
from alchemy.archive_models import *
from alchemy.setup import *

from alchemy.base_handlers import BaseHandler

logger = logging.getLogger("aswwu")

class AdministratorRoleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        if 'administrator' not in user.roles.split(','):
            self.write({'error': 'insufficient permissions'})
        else:
            cmd = self.get_argument('cmd', None)
            if cmd == 'set_role':
                username = 'taylor.haugen'#self.get_argument('username', '')
                logger.debug(username)
                fuser = s.query(User).filter_by(username=username).all()
                if not fuser:
                    self.write({'error': 'user does not exist'})
                else:
                    fuser = fuser[0]
                    roles = fuser.roles.split(',')
                    roles.append(self.get_argument('newRole', None))
                    roles = set(roles)
                    fuser.roles = (',').join(roles)
                    addOrUpdate(fuser)
                    self.write(json.dumps('success'))
