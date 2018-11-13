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


# Parameters: parameters (dict), required_parameters (tuple of strings)
# Checks that the required parameters are in the json dict
def checkParameters(given_parameters, required_parameters):
    if len(required_parameters) != len(list(given_parameters.keys())):
        raise Exception
    for parameter in required_parameters:
        if not given_parameters.has_key(parameter):
            raise Exception
    if given_parameters.has_key('election_type'):
        if given_parameters['election_type'] not in ('aswwu', 'senate'):
            raise Exception


class VoteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        votes = alchemy.query_vote(user.username)
        self.write({'votes': [v.serialize() for v in votes]})


class ElectionHandler(BaseHandler):
    def get(self):
        try:
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

            self.write({'elections': [e.serialize() for e in elections]})
        except Exception:
            self.set_status(400)
            self.write({"status": "error"})

    def post(self):
        # TODO: dont create new elections during another election
        # checking for required parameters
        try:
            required_parameters = ('election_type', 'start', 'end')
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)
            try:
                checkParameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            if alchemy.detect_election_overlap(body_json["start"], body_json["end"]):
                self.set_status(403)
                self.write({"status": "error"})
                return

            # create new election object
            election = elections_model.Election()
            for parameter in required_parameters:
                if parameter in ("start", "end"):
                    d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                    setattr(election, parameter, d)
                else:
                    setattr(election, parameter, body_json[parameter])
            alchemy.add_or_update(election)

            self.set_status(201)
            self.write(election.serialize())

        except Exception as e:
            logger.error("ElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class SpecifiedElectionHandler(BaseHandler):
    def get(self, election_id):
        try:
            position = alchemy.query_election(election_id=str(election_id))
            self.write(position[0].serialize())

        except Exception:
            self.set_status(404)
            self.write({"status": "error"})

    @tornado.web.authenticated
    def put(self, election_id):
        try:
            required_parameters = ('election_type', 'start', 'end')
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)

            # Checking for required parameters
            try:
                checkParameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            if alchemy.detect_election_overlap(body_json["start"], body_json["end"]):
                self.set_status(403)
                self.write({"status": "error"})
                return

            # fetch position
            try:
                election = alchemy.query_election(election_id=str(election_id))

            except Exception:
                self.set_status(404)
                self.write({"status": "error"})
                return

            election = election[0]

            for parameter in required_parameters:
                if parameter in ("start", "end"):
                    d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                    setattr(election, parameter, d)
                else:
                    setattr(election, parameter, body_json[parameter])
            alchemy.add_or_update(election)

            self.set_status(200)
            self.write(election.serialize())

        except Exception as e:
            logger.error("SpecifiedElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class CurrentHandler(BaseHandler):
    def get(self):
        election = alchemy.query_current()
        if election is None:
            self.set_status(404)
            self.write({'status': 'The resource could not be found.'})
            return
        self.write(election.serialize())



