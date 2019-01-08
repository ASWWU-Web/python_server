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
        try:
            user = self.current_user
            current_election = alchemy.query_current()
            if current_election is None:
                self.set_status(404)
                self.write({"status": "there is currently no open election"})
                return
            votes = alchemy.query_vote(election=current_election.id, username=str(user.username))
            self.write({'votes': [v.serialize() for v in votes]})
        except Exception as e:
            logger.error("VoteHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})

    @tornado.web.authenticated
    def post(self):
        try:
            user = self.current_user
            # load request body
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)
            # check body parameters
            required_parameters = ('election', 'position', 'vote')
            try:
                checkParameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return
            # validate parameters
            # check if election exists
            specified_election = alchemy.query_election(election_id=body_json['election'])
            if specified_election == list():
                self.set_status(404)
                self.write({"status": "election with specified ID not found"})
                return
            # check if not current election
            current_election = alchemy.query_current()
            if specified_election[0] != current_election:
                self.set_status(403)
                self.write({"status": "this election is not available for voting"})
                return
            # check if position exists and is active
            specified_position = alchemy.query_position(position_id=body_json['position'])
            if specified_position == list() or specified_position[0].active is False:
                self.set_status(404)
                self.write({"status": "position with specified ID not found"})
                return
            # check if position is the right election type
            if specified_position[0].election_type != current_election.election_type:
                self.set_status(403)
                self.write({"status": "you are voting for a position in a different election type"})
                return
            # check if vote for position in current election already exists
            if alchemy.query_vote(election=specified_election[0].id,
                                  position=specified_position[0].id,
                                  username=str(user.username)) != list():
                self.set_status(403)
                self.write({"status": "you have already voted for this position"})
                return
            # check if user has already voted in senate election
            if specified_election[0].election_type == 'senate' and \
                    alchemy.query_vote(election=specified_election[0].id, username=str(user.username)) != list():
                self.set_status(403)
                self.write({"status": "you can only vote for one senator"})
                return
            # create a new vote
            vote = elections_model.Vote()
            for parameter in required_parameters:
                setattr(vote, parameter, body_json[parameter])
            setattr(vote, 'username', str(user.username))
            alchemy.add_or_update(vote)
        except Exception as e:
            logger.error("VoteHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class SpecificVoteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, vote_id):
        try:
            user = self.current_user
            # get current election
            current_election = alchemy.query_current()
            if current_election is None:
                self.set_status(404)
                self.write({"status": "there is currently no open election"})
                return
            # get vote
            vote = alchemy.query_vote(vote_id=str(vote_id), election=current_election.id, username=str(user.username))
            if vote == list():
                self.set_status(404)
                self.write({"status": "vote with specified ID not found"})
                return
            self.write(vote[0].serialize())
        except Exception as e:
            logger.error("SpecificVoteHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})

    @tornado.web.authenticated
    def put(self, vote_id):
        try:
            user = self.current_user
            # load request body
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)
            # get current election
            current_election = alchemy.query_current()
            if current_election is None:
                self.set_status(404)
                self.write({"status": "there is currently no open election"})
                return
            # get vote
            vote = alchemy.query_vote(vote_id=vote_id, election=current_election.id, username=str(user.username))
            if vote == list():
                self.set_status(404)
                self.write({"status": "vote with specified ID not found"})
                return
            # check body parameters
            required_parameters = ('election', 'position', 'vote')
            try:
                checkParameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return
            # validate parameters
            # check if election exists
            specified_election = alchemy.query_election(election_id=body_json['election'])
            if specified_election == list():
                self.set_status(404)
                self.write({"status": "election with specified ID not found"})
                return
            # check if not current election
            current_election = alchemy.query_current()
            if specified_election[0] != current_election:
                self.set_status(403)
                self.write({"status": "this election is not available for voting"})
                return
            # check if position exists and is active
            specified_position = alchemy.query_position(position_id=body_json['position'])
            if specified_position == list() or specified_position[0].active is False:
                self.set_status(404)
                self.write({"status": "position with specified ID not found"})
                return
            # check if position is the right election type
            if specified_position[0].election_type != current_election.election_type:
                self.set_status(403)
                self.write({"status": "you are voting for a position in a different election type"})
                return
            # check if vote for position in current election already exists
            if alchemy.query_vote(election=specified_election[0].id,
                                  position=specified_position[0].id,
                                  username=str(user.username)) != list():
                self.set_status(403)
                self.write({"status": "you have already voted for this position"})
                return
            # check if user has already voted in senate election
            if specified_election[0].election_type == 'senate' and \
                    alchemy.query_vote(election=specified_election[0].id, username=str(user.username)) != list():
                self.set_status(403)
                self.write({"status": "you can only vote for one senator"})
                return
            # update vote
            for parameter in required_parameters:
                setattr(vote, parameter, body_json[parameter])
            setattr(vote, 'username', str(user.username))
            alchemy.add_or_update(vote)
        except Exception as e:
            logger.error("VoteHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


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
        election = alchemy.query_current_or_upcoming()
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
            positions = alchemy.query_position(position_id=search_criteria.get('id', None),
                                               position=search_criteria.get('position', None),
                                               election_type=search_criteria.get('election_type', None),
                                               active=search_criteria.get('active', None))
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
