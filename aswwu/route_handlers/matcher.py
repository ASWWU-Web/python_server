import logging

import tornado.web

from aswwu import BaseHandler

logger = logging.getLogger("aswwu")


class MatcherHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user

        if 'matcher' in user.roles:
            profiles = query_all(Profile)
            self.write({'database': [p.view_other() for p in profiles]})
        else:
            self.write("{'error': 'Insufficient Permissions :('}")
