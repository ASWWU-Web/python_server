import logging

import tornado.web
import json

from datetime import datetime

from aswwu.base_handlers import BaseHandler
import aswwu.alchemy_new.elections as elections_alchemy
import aswwu.alchemy_new.mask as mask_alchemy
import aswwu.models.elections as elections_model
import aswwu.exceptions as exceptions

logger = logging.getLogger("aswwu")

election_db = elections_alchemy.election_db


# Parameters: parameters (dict), required_parameters (tuple of strings)
# Checks that the required parameters are in the json dict
def validate_parameters(given_parameters, required_parameters):
    # check for missing parameters
    for parameter in required_parameters:
        if parameter not in given_parameters.keys():
            raise exceptions.BadRequest400Exception('missing parameters')
    # check for too many parameters
    if len(required_parameters) != len(list(given_parameters.keys())):
        raise exceptions.BadRequest400Exception('too many parameters')
    # check for bad election type
    if 'election_type' in given_parameters.keys() and given_parameters['election_type'] not in ('aswwu', 'senate'):
        raise exceptions.BadRequest400Exception('election_type is not aswwu or senate')


def validate_vote(user, parameters, existing_vote=None):
    # validate parameters
    # check if election exists
    specified_election = elections_alchemy.query_election(election_id=parameters['election'])
    if specified_election == list():
        raise exceptions.NotFound404Exception('election with specified ID not found')
    # check if not current election
    current_election = elections_alchemy.query_current()
    if specified_election[0] != current_election:
        raise exceptions.Forbidden403Exception('this election is not available for voting')
    # check if position exists and is active
    specified_position = elections_alchemy.query_position(position_id=parameters['position'])
    if specified_position == list() or specified_position[0].active is False:
        raise exceptions.Forbidden403Exception('position with specified ID not found')
    # check if position is the right election type
    if specified_position[0].election_type != current_election.election_type:
        raise exceptions.Forbidden403Exception('you are voting for a position in a different election type')
    # check for valid candidate username
    if mask_alchemy.query_by_username(parameters['vote']) is None:
        raise exceptions.Forbidden403Exception('you cannot vote for this person')
    # check amount of votes a user has in aswwu or senate election
    if existing_vote is None:
        if specified_election[0].election_type == 'aswwu' and \
                len(elections_alchemy.query_vote(election=specified_election[0].id,
                                                 position=specified_position[0].id,
                                                 username=str(user.username))) >= 1:
            raise exceptions.Forbidden403Exception('you can only vote for one aswwu representative')
        elif specified_election[0].election_type == 'senate' and \
                len(elections_alchemy.query_vote(election=specified_election[0].id,
                                                 position=specified_position[0].id,
                                                 username=str(user.username))) >= 2:
            raise exceptions.Forbidden403Exception('you can only vote for two senators')
    # check for duplicate votes
    if parameters['vote'] != getattr(existing_vote, 'vote', None) and \
            elections_alchemy.query_vote(election=specified_election[0].id,
                                         position=specified_position[0].id,
                                         vote=parameters['vote'],
                                         username=str(user.username)) != list():
        raise exceptions.Forbidden403Exception('you have already voted for this person')


class VoteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # Put query into JSON form
        search_criteria = {}
        query = self.request.arguments
        for key, value in query.items():
            search_criteria[key] = value[0]
        # request
        user = self.current_user
        current_election = elections_alchemy.query_current()
        if current_election is None:
            raise exceptions.NotFound404Exception('there is currently no open election')
        votes = elections_alchemy.query_vote(election=current_election.id,
                                             username=str(user.username),
                                             position=search_criteria.get('position', None),
                                             vote=search_criteria.get('vote', None))
        self.write({'votes': [v.serialize() for v in votes]})

    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)
        # check body parameters
        required_parameters = ('election', 'position', 'vote')
        validate_parameters(body_json, required_parameters)
        # validate vote
        validate_vote(user, body_json)
        # create a new vote
        vote = elections_model.Vote()
        for parameter in required_parameters:
            setattr(vote, parameter, body_json[parameter])
        setattr(vote, 'username', str(user.username))
        elections_alchemy.add_or_update(vote)
        # response
        self.set_status(201)
        self.write(vote.serialize())


class SpecificVoteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, vote_id):
        user = self.current_user
        # get current election
        current_election = elections_alchemy.query_current()
        if current_election is None:
            raise exceptions.Forbidden403Exception('there is currently no open election')
        # get vote
        vote = elections_alchemy.query_vote(vote_id=str(vote_id),
                                            election=current_election.id,
                                            username=str(user.username))
        # validate vote ID
        if vote == list():
            raise exceptions.NotFound404Exception('vote with specified ID not found')
        self.write(vote[0].serialize())

    @tornado.web.authenticated
    def put(self, vote_id):
        user = self.current_user
        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)
        # get current election
        current_election = elections_alchemy.query_current()
        if current_election is None:
            exceptions.Forbidden403Exception('there is currently no open election')
        # get vote
        vote = elections_alchemy.query_vote(vote_id=vote_id,
                                            election=current_election.id,
                                            username=str(user.username))
        if vote == list():
            raise exceptions.NotFound404Exception('vote with specified ID not found')
        # check body parameters
        required_parameters = ('id', 'election', 'position', 'vote', 'username')
        # validate parameters and vote
        validate_parameters(body_json, required_parameters)
        validate_vote(user, body_json, vote[0])
        # update vote
        for parameter in required_parameters:
            if parameter not in ('id', 'username'):
                setattr(vote[0], parameter, body_json[parameter])
        setattr(vote[0], 'username', str(user.username))
        elections_alchemy.add_or_update(vote[0])
        # response
        self.write(vote[0].serialize())


class ElectionHandler(BaseHandler):
    def get(self):
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

    def post(self):
        # checking for required parameters
        required_parameters = ('election_type', 'start', 'end')
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        validate_parameters(body_json, required_parameters)
        # checking to make sure new election doesn't overlap with current or upcoming elections
        if elections_alchemy.detect_election_overlap(body_json["start"], body_json["end"]):
            raise exceptions.Forbidden403Exception('election takes place during another election')
        # checking to make sure new election doesn't start time in the past
        if elections_alchemy.detect_election_start(body_json["start"], body_json["end"]):
            raise exceptions.Forbidden403Exception('election takes place during the past')
        # checking to make sure end time isn't less than start time
        if elections_alchemy.detect_bad_end(body_json["start"], body_json["end"]):
            raise exceptions.Forbidden403Exception('start time is after end time')

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


class SpecifiedElectionHandler(BaseHandler):
    def get(self, election_id):
        position = elections_alchemy.query_election(election_id=str(election_id))
        if position == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')
        self.write(position[0].serialize())

    @tornado.web.authenticated
    def put(self, election_id):
        required_parameters = ('election_type', 'start', 'end')
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # Checking for required parameters
        validate_parameters(body_json, required_parameters)

        if elections_alchemy.detect_election_overlap(body_json["start"], body_json["end"]):
            raise exceptions.Forbidden403Exception('')

        # fetch election
        election = elections_alchemy.query_election(election_id=str(election_id))
        if election == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')
        election = election[0]

        # set new values
        for parameter in required_parameters:
            if parameter in ("start", "end"):
                d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                setattr(election, parameter, d)
            else:
                setattr(election, parameter, body_json[parameter])
        elections_alchemy.add_or_update(election)

        self.write(election.serialize())


class CurrentHandler(BaseHandler):
    def get(self):
        election = elections_alchemy.query_current_or_upcoming()
        if election is None:
            raise exceptions.NotFound404Exception('there is no current or upcoming election')
        self.write(election.serialize())


class PositionHandler(BaseHandler):
    def get(self):
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

    @tornado.web.authenticated
    def post(self):
        required_parameters = ('position', 'election_type', 'active')
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # Checking for required parameters
        validate_parameters(body_json, required_parameters)

        # create new position
        position = elections_model.Position()
        for parameter in required_parameters:
            setattr(position, parameter, body_json[parameter])

        elections_alchemy.add_or_update(position)
        self.set_status(201)
        self.write(position.serialize())


class SpecifiedPositionHandler(BaseHandler):
    def get(self, position_id):
        position = elections_alchemy.query_position(position_id=str(position_id))
        if position == list():
            raise exceptions.NotFound404Exception('position with specified ID not found')
        self.write(position[0].serialize())

    @tornado.web.authenticated
    def put(self, position_id):
        required_parameters = ('position', 'election_type', 'active')
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # Checking for required parameters
        validate_parameters(body_json, required_parameters)

        # fetch position
        position = elections_alchemy.query_position(position_id=str(position_id))
        if position == list():
            raise exceptions.NotFound404Exception('position with specified ID not found')

        position = position[0]
        for parameter in required_parameters:
            setattr(position, parameter, body_json[parameter])

        elections_alchemy.add_or_update(position)
        self.write(position.serialize())


class CandidateHandler(BaseHandler):
    def get(self, election_id):
        search_criteria = {}
        # Put query into JSON form
        query = self.request.arguments
        for key, value in query.items():
            search_criteria[key] = value[0]
        if elections_alchemy.query_election(election_id=str(election_id)) == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')
        # query candidates from database
        candidates = elections_alchemy.query_candidates(position=search_criteria.get('position', None),
                                                        username=search_criteria.get('username', None),
                                                        display_name=search_criteria.get('display_name', None),
                                                        election_id=str(election_id))
        self.write({'candidates': [c.serialize() for c in candidates]})

    @tornado.web.authenticated
    def post(self, election_id):
        user = self.current_user
        # permission checking
        if 'election-admin' not in user.roles and 'administrator' not in user.roles:
            raise exceptions.Forbidden403Exception('you do not have permissions to do this')

        required_parameters = ('position', 'username', 'display_name')
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)
        validate_parameters(body_json, required_parameters)

        # checks to make sure there is an election to push candidates to
        election = elections_alchemy.query_election(election_id=str(election_id))
        if election == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')
        election = election[0]

        # checks to make sure election is either current of up and coming
        if election != elections_alchemy.query_current() and \
                election not in elections_alchemy.query_election(start=datetime.now()):
            raise exceptions.Forbidden403Exception('candidate not in current election')

        # checks to makes sure position exists
        if not elections_alchemy.query_position(position_id=str(body_json["position"])):
            raise exceptions.NotFound404Exception('position with specified ID not found')

        # checks to make sure election exists
        if not elections_alchemy.query_election(election_id=str(election_id)):
            raise exceptions.NotFound404Exception('election with specified ID not found')

        # create new candidate object
        candidate = elections_model.Candidate()
        for parameter in required_parameters:
            setattr(candidate, parameter, body_json[parameter])
        candidate.election = str(election_id)
        elections_alchemy.add_or_update(candidate)

        self.set_status(201)
        self.write(candidate.serialize())


class SpecifiedCandidateHandler(BaseHandler):
    def get(self, election_id, candidate_id):
        # checks to make sure there is a candidate to query
        if elections_alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id)) == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')

        # queries candidate
        candidate = elections_alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))
        self.write(candidate[0].serialize())

    @tornado.web.authenticated
    def put(self, election_id, candidate_id):
            user = self.current_user
            # permission checking
            if 'election-admin' not in user.roles and 'administrator' not in user.roles:
                raise exceptions.Forbidden403Exception('you do not have permissions to do this')

            required_parameters = ('election', 'position', 'username', 'display_name')
            body = self.request.body.decode('utf-8')
            body_json = json.loads(body)

            # Checking for required parameters
            validate_parameters(body_json, required_parameters)

            # checks to makes sure position exists
            if not elections_alchemy.query_position(position_id=str(body_json["position"])):
                raise exceptions.NotFound404Exception('position with specified ID not found')

            # checks to make sure election exists
            if not elections_alchemy.query_election(election_id=str(election_id)):
                raise exceptions.NotFound404Exception('election with specified ID not found')

            # checks to make sure there is a candidate to query
            if len(elections_alchemy.query_candidates(election_id=str(election_id),
                                                      candidate_id=str(candidate_id))) is 0:
                raise exceptions.NotFound404Exception('candidate with specified ID not found')

            # fetch position
            candidate = elections_alchemy.query_candidates(election_id=str(election_id),
                                                           candidate_id=str(candidate_id))

            election = elections_alchemy.query_election(election_id=str(election_id))[0]

            # checks to see if candidate is in current election
            if election != elections_alchemy.query_current() and election not in elections_alchemy.query_election(
                    start=datetime.now()):
                raise exceptions.Forbidden403Exception('specified candidate is not in the current election')
            candidate = candidate[0]

            for parameter in required_parameters:
                setattr(candidate, parameter, body_json[parameter])
            elections_alchemy.add_or_update(candidate)

            self.write(candidate.serialize())

    @tornado.web.authenticated
    def delete(self, election_id, candidate_id):
        user = self.current_user
        # permission checking
        if 'election-admin' not in user.roles and 'administrator' not in user.roles:
            raise exceptions.Forbidden403Exception('you do not have permissions to do this')
        # get the candidate from the database
        candidate = elections_alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))
        if len(candidate) == 0:
            raise exceptions.NotFound404Exception('candidate with specified ID not found')
        candidate = candidate[0]
        # dont allow deleting past candidates
        election = elections_alchemy.query_election(election_id=str(election_id))
        if len(election) == 0:
            raise exceptions.NotFound404Exception('election with specified ID not found')
        if election[0] != elections_alchemy.query_current() and election[0] not in elections_alchemy.query_election(
                start=datetime.now()):
            raise exceptions.Forbidden403Exception('candidate not in the current election')
        # delete the candidate
        elections_alchemy.delete(candidate)
        self.set_status(204)
