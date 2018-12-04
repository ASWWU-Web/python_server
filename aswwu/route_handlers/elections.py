import logging

import tornado.web
import json

from datetime import datetime

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

            # checking to make sure new election doesn't overlap with current or upcoming elections
            if alchemy.detect_election_overlap(body_json["start"], body_json["end"]):
                self.set_status(403)
                self.write({"status": "error"})
                return

            # checking to make sure new election doesn't start time in the past
            if alchemy.detect_election_start(body_json["start"], body_json["end"]):
                self.set_status(403)
                self.write({"status": "error"})
                return

            # checking to make sure end time isn't less than start time
            if alchemy.detect_bad_end(body_json["start"], body_json["end"]):
                self.set_status(400)
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


class PositionHandler(BaseHandler):
    def get(self):
        try:
            search_criteria = {}
            # Put query into JSON form
            query = self.request.arguments
            for key, value in query.items():
                search_criteria[key] = value[0]
            positions = alchemy.query_position(position_id= search_criteria.get('id', None), position = search_criteria.get('position', None), election_type = search_criteria.get('election_type', None), active = search_criteria.get('active', None))
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
            position = alchemy.query_position(position_id=str(position_id))
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
                position = alchemy.query_position(position_id=str(position_id))

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


class CandidateHandler(BaseHandler):
    def get(self, election_id):
        try:
            search_criteria = {}
            # Put query into JSON form
            query = self.request.arguments
            for key, value in query.items():
                search_criteria[key] = value[0]
            if not alchemy.query_election(election_id=str(election_id)):
                self.set_status(404)
                self.write({"status": "election doesn't exist"})
                return
            # query candidates from database
            candidates = alchemy.query_candidates(position=search_criteria.get('position', None),
                                                  username=search_criteria.get('username', None),
                                                  display_name=search_criteria.get('display_name', None),
                                                  election_id=str(election_id))

            self.write({'candidates': [c.serialize() for c in candidates]})
        except Exception:
            self.set_status(400)
            self.write({"status": "error"})

    @tornado.web.authenticated
    def post(self, election_id):
        try:
            user = self.current_user
            # permission checking
            if 'election-admin' not in user.roles and 'administrator' not in user.roles:
                self.set_status(403)
                self.write({"status": "This action requires authorization or is not allowed."})
                return

            required_parameters = ('position', 'username', 'display_name')
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)
            try:
                checkParameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            try:
                election = alchemy.query_election(election_id=str(election_id))[0]
                if election != alchemy.query_current() and election not in alchemy.query_election(start=datetime.now()):
                    self.set_status(403)
                    self.write({"status": "Candidate not in current election"})
                    return

            except Exception:
                self.set_status(404)
                self.write({"status": "error"})
                return

            # checks to makes sure position exists
            if not alchemy.query_position(position_id=str(body_json["position"])):
                self.set_status(404)
                self.write({"status": "position doesn't exist"})
                return

            # checks to make sure election exists
            if not alchemy.query_election(election_id=str(election_id)):
                self.set_status(404)
                self.write({"status": "election doesn't exist"})
                return

            # create new candidate object
            candidate = elections_model.Candidate()
            for parameter in required_parameters:
                setattr(candidate, parameter, body_json[parameter])
            candidate.election = str(election_id)
            alchemy.add_or_update(candidate)

            self.set_status(201)
            self.write(candidate.serialize())

        except Exception as e:
            logger.error("ElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class SpecifiedCandidateHandler(BaseHandler):
    def get(self, election_id, candidate_id):
        try:
            candidate = alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))
            self.write(candidate[0].serialize())

        except Exception:
            self.set_status(404)
            self.write({"status": "error"})

    @tornado.web.authenticated
    def put(self, election_id, candidate_id):
        try:
            user = self.current_user
            # permission checking
            if 'election-admin' not in user.roles and 'administrator' not in user.roles:
                self.set_status(403)
                self.write({"status": "This action requires authorization or is not allowed."})
                return

            required_parameters = ('election', 'position', 'username', 'display_name')
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)

            # Checking for required parameters
            try:
                checkParameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            # checks to makes sure position exists
            print(alchemy.query_position(position_id=str(body_json["position"])))
            if not alchemy.query_position(position_id=str(body_json["position"])):
                self.set_status(404)
                self.write({"status": "position doesn't exist"})
                return

            # checks to make sure election exists
            if not alchemy.query_election(election_id=str(election_id)):
                self.set_status(404)
                self.write({"status": "election doesn't exist"})
                return

            # fetch position
            try:
                candidate = alchemy.query_candidates(election_id=str(election_id),
                                                     candidate_id=str(candidate_id))

            except Exception:
                self.set_status(404)
                self.write({"status": "error"})
                return

            # checks to see if candidate is in current election
            try:
                election = alchemy.query_election(election_id=str(election_id))[0]
                if election != alchemy.query_current() and election not in alchemy.query_election(start=datetime.now()):
                    self.set_status(403)
                    self.write({"status": "Candidate not in current election"})
                    return

            except Exception:
                self.set_status(404)
                self.write({"status": "error"})
                return

            candidate = candidate[0]

            for parameter in required_parameters:
                setattr(candidate, parameter, body_json[parameter])
            alchemy.add_or_update(candidate)

            self.set_status(200)
            self.write(candidate.serialize())

        except Exception as e:
            logger.error("SpecifiedElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})

    @tornado.web.authenticated
    def delete(self, election_id, candidate_id):
        try:
            user = self.current_user
            # permission checking
            if 'election-admin' not in user.roles and 'administrator' not in user.roles:
                self.set_status(403)
                self.write({"status": "This action requires authorization or is not allowed."})
                return
            # get the candidate from the database
            candidate = alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))
            if len(candidate) == 0:
                self.set_status(404)
                self.write({"status": "error"})
                return
            if len(candidate) != 1:
                raise Exception('more than one candidate found with same ID')
            candidate = candidate[0]
            # dont allow deleting past candidates
            election = alchemy.query_election(election_id=str(election_id))
            if len(election) == 0:
                self.set_status(404)
                self.write({"status": "error"})
                return
            if len(election) != 1:
                raise Exception('more than one election found with same ID')
            if election[0] != alchemy.query_current() and election[0] not in alchemy.query_election(start=datetime.now()):
                self.set_status(403)
                self.write({"status": "Candidate not in current election"})
                return
            # delete the candidate
            alchemy.delete(candidate)
            # self.write(candidate.serialize())
            self.set_status(204)

        except Exception as e:
            logger.error("SpecifiedElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})
