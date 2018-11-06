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


class ElectionHandler(BaseHandler):
    def get(self):
        search_criteria = {}
        # Put query into JSON form
        query = self.request.arguments
        for key, value in query.items():
            search_criteria[key] = value[0]
        elections = alchemy.query_election(election_type=search_criteria.get('election_type', None),
                                           start=search_criteria.get('start', None),
                                           end=search_criteria.get('end', None))

        self.write({'elections': [e.serialize() for e in elections]})

