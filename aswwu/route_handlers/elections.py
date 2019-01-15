import logging

import tornado.web
import json

from datetime import datetime

from aswwu.base_handlers import BaseHandler
import aswwu.alchemy_new.elections as elections_alchemy
import aswwu.alchemy_new.mask as mask_alchemy
import aswwu.models.elections as elections_model
import aswwu.exceptions as http_exceptions

logger = logging.getLogger("aswwu")

election_db = elections_alchemy.election_db


# Parameters: parameters (dict), required_parameters (tuple of strings)
# Checks that the required parameters are in the json dict
def validate_parameters(given_parameters, required_parameters):
    if len(required_parameters) != len(list(given_parameters.keys())):
        raise Exception
    for parameter in required_parameters:
        if not given_parameters.has_key(parameter):
            raise Exception
    if given_parameters.has_key('election_type'):
        if given_parameters['election_type'] not in ('aswwu', 'senate'):
            raise Exception


def validate_vote(user, parameters, existing_vote=None):
    # validate parameters
    # check if election exists
    specified_election = elections_alchemy.query_election(election_id=parameters['election'])
    if specified_election == list():
        raise http_exceptions.NotFound404Exception('election with specified ID not found')
    # check if not current election
    current_election = elections_alchemy.query_current()
    if specified_election[0] != current_election:
        raise http_exceptions.Forbidden403Exception('this election is not available for voting')
    # check if position exists and is active
    specified_position = elections_alchemy.query_position(position_id=parameters['position'])
    if specified_position == list() or specified_position[0].active is False:
        raise http_exceptions.Forbidden403Exception('position with specified ID not found')
    # check if position is the right election type
    if specified_position[0].election_type != current_election.election_type:
        raise http_exceptions.Forbidden403Exception('you are voting for a position in a different election type')
    # check for valid candidate username
    if mask_alchemy.query_by_username(parameters['vote']) is None:
        raise http_exceptions.Forbidden403Exception('you cannot vote for this person')
    # check amount of votes a user has in aswwu or senate election
    if existing_vote is None:
        if specified_election[0].election_type == 'aswwu' and \
                len(elections_alchemy.query_vote(election=specified_election[0].id,
                                                 position=specified_position[0].id,
                                                 username=str(user.username))) >= 1:
            raise http_exceptions.Forbidden403Exception('you can only vote for one aswwu representative')
        elif specified_election[0].election_type == 'senate' and \
                len(elections_alchemy.query_vote(election=specified_election[0].id,
                                                 position=specified_position[0].id,
                                                 username=str(user.username))) >= 2:
            raise http_exceptions.Forbidden403Exception('you can only vote for two senators')
    # check for duplicate votes
    if parameters['vote'] != getattr(existing_vote, 'vote', None) and \
            elections_alchemy.query_vote(election=specified_election[0].id,
                                         position=specified_position[0].id,
                                         vote=parameters['vote'],
                                         username=str(user.username)) != list():
        raise http_exceptions.Forbidden403Exception('you have already voted for this person')


class VoteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            # Put query into JSON form
            search_criteria = {}
            query = self.request.arguments
            for key, value in query.items():
                search_criteria[key] = value[0]
            # request
            user = self.current_user
            current_election = elections_alchemy.query_current()
            if current_election is None:
                self.set_status(404)
                self.write({"status": "there is currently no open election"})
                return
            votes = elections_alchemy.query_vote(election=current_election.id,
                                                 username=str(user.username),
                                                 position=search_criteria.get('position', None),
                                                 vote=search_criteria.get('vote', None))
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
                validate_parameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return
            # validate vote
            try:
                validate_vote(user, body_json)
            except http_exceptions.Forbidden403Exception as e:
                self.set_status(403)
                self.write({"status": str(e)})
                return
            except http_exceptions.NotFound404Exception as e:
                self.set_status(404)
                self.write({"status": str(e)})
                return
            # create a new vote
            vote = elections_model.Vote()
            for parameter in required_parameters:
                setattr(vote, parameter, body_json[parameter])
            setattr(vote, 'username', str(user.username))
            elections_alchemy.add_or_update(vote)
            # response
            self.set_status(201)
            self.write(vote.serialize())
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
            current_election = elections_alchemy.query_current()
            if current_election is None:
                self.set_status(404)
                self.write({"status": "there is currently no open election"})
                return
            # get vote
            vote = elections_alchemy.query_vote(vote_id=str(vote_id), election=current_election.id,
                                                username=str(user.username))
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
            current_election = elections_alchemy.query_current()
            if current_election is None:
                self.set_status(404)
                self.write({"status": "there is currently no open election"})
                return
            # get vote
            vote = elections_alchemy.query_vote(vote_id=vote_id,
                                                election=current_election.id,
                                                username=str(user.username))
            if vote == list():
                self.set_status(404)
                self.write({"status": "vote with specified ID not found"})
                return
            # check body parameters
            required_parameters = ('id', 'election', 'position', 'vote', 'username')
            try:
                validate_parameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return
            # validate vote
            try:
                validate_vote(user, body_json, vote[0])
            except http_exceptions.Forbidden403Exception as e:
                self.set_status(403)
                self.write({"status": str(e)})
                return
            except http_exceptions.NotFound404Exception as e:
                self.set_status(404)
                self.write({"status": str(e)})
                return
            # update vote
            for parameter in required_parameters:
                if parameter not in ('id', 'username'):
                    setattr(vote[0], parameter, body_json[parameter])
            setattr(vote[0], 'username', str(user.username))
            elections_alchemy.add_or_update(vote[0])
            # response
            self.write(vote[0].serialize())
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
            elections = elections_alchemy.query_election(election_type=search_criteria.get('election_type', None),
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
                validate_parameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            # checking to make sure new election doesn't overlap with current or upcoming elections
            if elections_alchemy.detect_election_overlap(body_json["start"], body_json["end"]):
                self.set_status(403)
                self.write({"status": "error"})
                return

            # checking to make sure new election doesn't start time in the past
            if elections_alchemy.detect_election_start(body_json["start"], body_json["end"]):
                self.set_status(403)
                self.write({"status": "error"})
                return

            # checking to make sure end time isn't less than start time
            if elections_alchemy.detect_bad_end(body_json["start"], body_json["end"]):
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
            elections_alchemy.add_or_update(election)

            self.set_status(201)
            self.write(election.serialize())

        except Exception as e:
            logger.error("ElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class SpecifiedElectionHandler(BaseHandler):
    def get(self, election_id):
        try:
            position = elections_alchemy.query_election(election_id=str(election_id))
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
                validate_parameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            if elections_alchemy.detect_election_overlap(body_json["start"], body_json["end"]):
                self.set_status(403)
                self.write({"status": "error"})
                return

            # fetch position
            try:
                election = elections_alchemy.query_election(election_id=str(election_id))

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
            elections_alchemy.add_or_update(election)

            self.set_status(200)
            self.write(election.serialize())

        except Exception as e:
            logger.error("SpecifiedElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class CurrentHandler(BaseHandler):
    def get(self):
        election = elections_alchemy.query_current_or_upcoming()
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
            positions = elections_alchemy.query_position(position_id=search_criteria.get('id', None),
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
                validate_parameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            # create new position
            position = elections_model.Position()
            for parameter in required_parameters:
                setattr(position, parameter, body_json[parameter])

            elections_alchemy.add_or_update(position)
            self.set_status(201)
            self.write(position.serialize())

        except Exception as e:
            logger.error("PositionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class SpecifiedPositionHandler(BaseHandler):
    def get(self, position_id):
        try:
            position = elections_alchemy.query_position(position_id=str(position_id))
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
                validate_parameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            # fetch position
            try:
                position = elections_alchemy.query_position(position_id=str(position_id))

            except Exception:
                self.set_status(404)
                self.write({"status": "error"})
                return

            position = position[0]

            for parameter in required_parameters:
                setattr(position, parameter, body_json[parameter])

            elections_alchemy.add_or_update(position)
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
            if not elections_alchemy.query_election(election_id=str(election_id)):
                self.set_status(404)
                self.write({"status": "election doesn't exist"})
                return
            # query candidates from database
            candidates = elections_alchemy.query_candidates(position=search_criteria.get('position', None),
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
                validate_parameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            # checks to make sure there is an election to push candidates to
            if len(elections_alchemy.query_election(election_id=str(election_id))) is 0:
                self.set_status(404)
                self.write({"status": "election doesn't exist"})
                return

            election = elections_alchemy.query_election(election_id=str(election_id))[0]

            # checks to make sure election is either current of up and coming
            if election != elections_alchemy.query_current() and election not in elections_alchemy.query_election(
                    start=datetime.now()):
                self.set_status(403)
                self.write({"status": "Candidate not in current election"})
                return

            # checks to makes sure position exists
            if not elections_alchemy.query_position(position_id=str(body_json["position"])):
                self.set_status(404)
                self.write({"status": "position doesn't exist"})
                return

            # checks to make sure election exists
            if not elections_alchemy.query_election(election_id=str(election_id)):
                self.set_status(404)
                self.write({"status": "election doesn't exist"})
                return

            # create new candidate object
            candidate = elections_model.Candidate()
            for parameter in required_parameters:
                setattr(candidate, parameter, body_json[parameter])
            candidate.election = str(election_id)
            elections_alchemy.add_or_update(candidate)

            self.set_status(201)
            self.write(candidate.serialize())

        except Exception as e:
            logger.error("ElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})


class SpecifiedCandidateHandler(BaseHandler):
    def get(self, election_id, candidate_id):

        # checks to make sure there is a candidate to query
        if len(elections_alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))) is 0:
            self.set_status(404)
            self.write({"status": "candidate doesn't exist"})
            return

        # queries candidate
        candidate = elections_alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))
        self.write(candidate[0].serialize())

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
                validate_parameters(body_json, required_parameters)
            except Exception:
                self.set_status(400)
                self.write({"status": "error"})
                return

            # checks to makes sure position exists
            print(elections_alchemy.query_position(position_id=str(body_json["position"])))
            if not elections_alchemy.query_position(position_id=str(body_json["position"])):
                self.set_status(404)
                self.write({"status": "position doesn't exist"})
                return

            # checks to make sure election exists
            if not elections_alchemy.query_election(election_id=str(election_id)):
                self.set_status(404)
                self.write({"status": "election doesn't exist"})
                return

            # checks to make sure there is a candidate to query
            if len(elections_alchemy.query_candidates(election_id=str(election_id),
                                                      candidate_id=str(candidate_id))) is 0:
                self.set_status(404)
                self.write({"status": "candidate doesn't exist"})
                return

            # fetch position
            candidate = elections_alchemy.query_candidates(election_id=str(election_id),
                                                           candidate_id=str(candidate_id))

            # checks to make sure there is an election
            if len(elections_alchemy.query_election(election_id=str(election_id))) is 0:
                self.set_status(404)
                self.write({"status": "election doesn't exist"})
                return

            election = elections_alchemy.query_election(election_id=str(election_id))[0]

            # checks to see if candidate is in current election
            if election != elections_alchemy.query_current() and election not in elections_alchemy.query_election(
                    start=datetime.now()):
                self.set_status(403)
                self.write({"status": "Candidate not in current election"})
                return

            candidate = candidate[0]

            for parameter in required_parameters:
                setattr(candidate, parameter, body_json[parameter])
            elections_alchemy.add_or_update(candidate)

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
            candidate = elections_alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))
            if len(candidate) == 0:
                self.set_status(404)
                self.write({"status": "error"})
                return
            if len(candidate) != 1:
                raise Exception('more than one candidate found with same ID')
            candidate = candidate[0]
            # dont allow deleting past candidates
            election = elections_alchemy.query_election(election_id=str(election_id))
            if len(election) == 0:
                self.set_status(404)
                self.write({"status": "error"})
                return
            if len(election) != 1:
                raise Exception('more than one election found with same ID')
            if election[0] != elections_alchemy.query_current() and election[0] not in elections_alchemy.query_election(
                    start=datetime.now()):
                self.set_status(403)
                self.write({"status": "Candidate not in current election"})
                return
            # delete the candidate
            elections_alchemy.delete(candidate)
            # self.write(candidate.serialize())
            self.set_status(204)

        except Exception as e:
            logger.error("SpecifiedElectionHandler: error.\n" + str(e.message))
            self.set_status(500)
            self.write({"status": "error"})
