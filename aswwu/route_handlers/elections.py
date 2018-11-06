import logging

import tornado.web
import json

import bleach

from aswwu.base_handlers import BaseHandler
import aswwu.alchemy_new.elections as alchemy
import aswwu.models.elections as election_model

logger = logging.getLogger("aswwu")

election_db = alchemy.election_db


class VoteHandler(BaseHandler):
    # @tornado.web.authenticated
    def get(self):
        user = self.current_user
        votes = alchemy.query_vote(user.username)
        self.write({'votes': [v.serialize() for v in votes]})
