import logging

import tornado.web
import json

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
    if given_parameters.has_key('active'):
        if given_parameters['active'] not in (True, False):
            raise Exception


class VoteHandler(BaseHandler):
    # @tornado.web.authenticated
    def get(self):
        user = self.current_user
        votes = alchemy.query_vote(user.username)
        self.write({'votes': [v.serialize() for v in votes]})

class PositionHandler(BaseHandler):
    def get(self):
        try:
            search_criteria = {}
            # Put query into JSON form
            query = self.request.arguments
            for key, value in query.items():
                search_criteria[key] = value[0]
            positions = alchemy.query_position(id = search_criteria.get('id', None), position = search_criteria.get('position', None), election_type = search_criteria.get('election_type', None), active = search_criteria.get('active', None))
            self.write({'positions': [p.serialize() for p in positions]})
        except Exception as e:
            logger.error("PositionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})

    @tornado.web.authenticated
    def post(self):
        try:
            required_parameters = ('position', 'election_type', 'active')
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)

            # Checking for required parameters
            try:
                checkParameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            # create new position
            position = elections_model.Position()
            for parameter in required_parameters:
                setattr(position, parameter, body_json[parameter])

            alchemy.add_or_update(position)
            self.set_status(201)
            self.write(position.serialize())

        except Exception as e:
            logger.error("PositionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class SpecifiedPositionHandler(BaseHandler):
    def get(self, position_id):
        try:
            position = alchemy.query_position(id=str(position_id))
            self.write(position[0].serialize())

        except Exception:
            self.set_status(404)
            self.write({"status": "error"})

    @tornado.web.authenticated
    def put(self, position_id):
        try:
            required_parameters = ('position', 'election_type', 'active')
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)

            # Checking for required parameters
            try:
                checkParameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            # fetch position
            try:
                position = alchemy.query_position(id=str(position_id))

            except Exception:
                self.set_status(404)
                self.write({"status": "error"})
                return

            position = position[0]

            for parameter in required_parameters:
                setattr(position, parameter, body_json[parameter])

            alchemy.add_or_update(position)
            self.set_status(200)
            self.write(position.serialize())

        except Exception as e:
            logger.error("PositionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})





