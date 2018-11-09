import logging

import tornado.web
import json

from datetime import datetime

import bleach

from aswwu.base_handlers import BaseHandler
import aswwu.alchemy_new.elections as alchemy
import aswwu.models.elections as elections_model

logger = logging.getLogger("aswwu")

election_db = alchemy.election_db


class VoteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        votes = alchemy.query_vote(user.username)
        self.write({'votes': [v.serialize() for v in votes]})


class ElectionHandler(BaseHandler):
    def get(self):
        # TODO put this in a try
        search_criteria = {}
        # Put query into JSON form
        query = self.request.arguments
        for key, value in query.items():
            search_criteria[key] = value[0]
            if key in ('start', 'end'):
                search_criteria[key] = datetime.strptime(search_criteria.get(key), '%Y-%m-%d %H:%M:%S.%f')
        elections = alchemy.query_election(election_type=search_criteria.get('election_type', None),
                                           start=search_criteria.get('start', None),
                                           end=search_criteria.get('end', None))

        self.write({'elections': [e.to_json() for e in elections]})

    def post(self):
        # TODO: dont create new elections during another election
        # checking for required parameters
        try:
            required_parameters = ('election_type', 'start', 'end')
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)
            try:
                if len(required_parameters) != len(list(body_json.keys())):
                    raise Exception
                for parameter in required_parameters:
                    if not body_json.has_key(parameter):
                        raise Exception
                if body_json['election_type'] not in ('aswwu', 'senate'):
                    raise Exception
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            # create new election object
            election = elections_model.Election()
            # TODO: cast datetime string to datetime object
            # for parameter in required_parameters:
            #     setattr(election, parameter, body_json[parameter])
            election.election_type = 'aswwu'
            election.start = datetime.now()
            election.end = datetime.now()
            alchemy.add_or_update(election)

            self.set_status(201)
            self.write(election.to_json())

        except Exception as e:
            logger.error("ElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class CurrentHandler(BaseHandler):
    def get(self):
        election = alchemy.query_current()
        if election is None:
            self.set_status(404)
            self.write({'status': 'The resource could not be found.'})
            return
        self.write(election.to_json())



