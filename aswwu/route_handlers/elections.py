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


def validate_election(parameters):
    # check that election doesn't overlap with current or upcoming elections
    if elections_alchemy.detect_election_overlap(parameters["start"], parameters["end"]):
        raise exceptions.Forbidden403Exception('election takes place during another election')
    # checking that election doesn't start time in the past
    if elections_alchemy.detect_election_start(parameters["start"], parameters["end"]):
        raise exceptions.Forbidden403Exception('election takes place during the past')
    # check that end time isn't less than start time
    if elections_alchemy.detect_bad_end(parameters["start"], parameters["end"]):
        raise exceptions.Forbidden403Exception('start time is after end time')


def validate_position(parameters):
    if not isinstance(parameters['active'], bool):
        raise exceptions.BadRequest400Exception('parameter active has type bool')


def validate_candidate(parameters, election_id):
    # check to make sure there is an election to push candidates to
    election = elections_alchemy.query_election(election_id=str(election_id))
    if election == list():
        raise exceptions.NotFound404Exception('election with specified ID not found')
    election = election[0]

    # check to make sure election is either current or up and coming
    if election != elections_alchemy.query_current() and \
            election not in elections_alchemy.query_election(start=datetime.now()):
        raise exceptions.Forbidden403Exception('candidate not in current election')

    # check to makes sure position exists
    if not elections_alchemy.query_position(position_id=str(parameters["position"])):
        raise exceptions.NotFound404Exception('position with specified ID not found')

    # check to make sure election exists
    if not elections_alchemy.query_election(election_id=str(election_id)):
        raise exceptions.NotFound404Exception('election with specified ID not found')


def check_permissions(user):
    if 'elections-admin' not in user.roles and 'administrator' not in user.roles:
        raise exceptions.Forbidden403Exception('you do not have permissions to do this')


def build_query_params(request_arguments):
    search_criteria = {}
    for key, value in request_arguments.items():
        if key in ('start', 'end'):
            search_criteria[key] = datetime.strptime(search_criteria.get(key), '%Y-%m-%d %H:%M:%S.%f')
        else:
            search_criteria[key] = value[0]
    return search_criteria


class VoteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # get current user
        user = self.current_user

        # build query parameter dict
        search_criteria = build_query_params(self.request.arguments)

        # get current election
        current_election = elections_alchemy.query_current()
        if current_election is None:
            raise exceptions.NotFound404Exception('there is currently no open election')

        # get votes
        votes = elections_alchemy.query_vote(election=current_election.id,
                                             username=str(user.username),
                                             position=search_criteria.get('position', None),
                                             vote=search_criteria.get('vote', None))

        # response
        self.set_status(200)
        self.write({'votes': [v.serialize() for v in votes]})

    @tornado.web.authenticated
    def post(self):
        # get current user
        user = self.current_user

        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('election', 'position', 'vote')
        validate_parameters(body_json, required_parameters)
        validate_vote(user, body_json)

        # create new vote
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
        # get current user
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

        # response
        self.set_status(200)
        self.write(vote[0].serialize())

    @tornado.web.authenticated
    def put(self, vote_id):
        # get current user
        user = self.current_user

        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # get current election
        current_election = elections_alchemy.query_current()
        if current_election is None:
            exceptions.Forbidden403Exception('there is currently no open election')

        # get vote
        vote = elections_alchemy.query_vote(vote_id=vote_id, election=current_election.id, username=str(user.username))
        if vote == list():
            raise exceptions.NotFound404Exception('vote with specified ID not found')

        # validate parameters
        required_parameters = ('id', 'election', 'position', 'vote', 'username')
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
        # build query parameter dict
        search_criteria = build_query_params(self.request.arguments)

        # get election
        elections = elections_alchemy.query_election(election_type=search_criteria.get('election_type', None),
                                                     start=search_criteria.get('start', None),
                                                     end=search_criteria.get('end', None))

        # response
        self.set_status(200)
        self.write({'elections': [e.serialize() for e in elections]})

    @tornado.web.authenticated
    def post(self):
        # get current user and check permissions
        user = self.current_user
        check_permissions(user)

        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('election_type', 'start', 'end')
        validate_parameters(body_json, required_parameters)
        validate_election(body_json)

        # create new election
        election = elections_model.Election()
        for parameter in required_parameters:
            if parameter in ("start", "end"):
                d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                setattr(election, parameter, d)
            else:
                setattr(election, parameter, body_json[parameter])
        elections_alchemy.add_or_update(election)

        # response
        self.set_status(201)
        self.write(election.serialize())


class SpecifiedElectionHandler(BaseHandler):
    def get(self, election_id):
        # get election
        election = elections_alchemy.query_election(election_id=str(election_id))
        if election == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')

        # response
        self.set_status(200)
        self.write(election[0].serialize())

    @tornado.web.authenticated
    def put(self, election_id):
        # get current user and check permissions
        user = self.current_user
        check_permissions(user)

        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # get current election
        election = elections_alchemy.query_election(election_id=str(election_id))
        if election == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')
        election = election[0]

        # validate parameters
        required_parameters = ('id', 'election_type', 'start', 'end')
        validate_parameters(body_json, required_parameters)
        validate_election(body_json)

        # update election
        for parameter in required_parameters:
            if parameter in ("start", "end"):
                d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                setattr(election, parameter, d)
            else:
                setattr(election, parameter, body_json[parameter])
        elections_alchemy.add_or_update(election)

        # response
        self.write(election.serialize())


class CurrentHandler(BaseHandler):
    def get(self):
        # get election
        election = elections_alchemy.query_current_or_upcoming()
        if election is None:
            raise exceptions.NotFound404Exception('there is no current or upcoming election')

        # response
        self.set_status(200)
        self.write(election.serialize())


class PositionHandler(BaseHandler):
    def get(self):
        # build query parameter dict
        search_criteria = build_query_params(self.request.arguments)

        # get positions
        positions = elections_alchemy.query_position(position=search_criteria.get('position', None),
                                                     election_type=search_criteria.get('election_type', None),
                                                     active=search_criteria.get('active', None))

        # response
        self.set_status(200)
        self.write({'positions': [p.serialize() for p in positions]})

    @tornado.web.authenticated
    def post(self):
        # get current user and check permissions
        user = self.current_user
        check_permissions(user)

        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('position', 'election_type', 'active')
        validate_parameters(body_json, required_parameters)
        validate_position(body_json)

        # create new position
        position = elections_model.Position()
        for parameter in required_parameters:
            setattr(position, parameter, body_json[parameter])
        elections_alchemy.add_or_update(position)

        # response
        self.set_status(201)
        self.write(position.serialize())


class SpecifiedPositionHandler(BaseHandler):
    def get(self, position_id):
        # get position
        position = elections_alchemy.query_position(position_id=str(position_id))
        if position == list():
            raise exceptions.NotFound404Exception('position with specified ID not found')

        # response
        self.set_status(200)
        self.write(position[0].serialize())

    @tornado.web.authenticated
    def put(self, position_id):
        # get current user and check permissions
        user = self.current_user
        check_permissions(user)

        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('id', 'position', 'election_type', 'active')
        validate_parameters(body_json, required_parameters)
        validate_position(body_json)

        # get position
        position = elections_alchemy.query_position(position_id=str(position_id))
        if position == list():
            raise exceptions.NotFound404Exception('position with specified ID not found')
        position = position[0]

        # update position
        for parameter in required_parameters:
            setattr(position, parameter, body_json[parameter])
        elections_alchemy.add_or_update(position)

        # response
        self.set_status(200)
        self.write(position.serialize())


class CandidateHandler(BaseHandler):
    def get(self, election_id):
        # build query parameter dict
        search_criteria = build_query_params(self.request.arguments)

        # get election
        if elections_alchemy.query_election(election_id=str(election_id)) == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')

        # get candidates
        candidates = elections_alchemy.query_candidates(election_id=str(election_id),
                                                        position=search_criteria.get('position', None),
                                                        username=search_criteria.get('username', None),
                                                        display_name=search_criteria.get('display_name', None))

        # response
        self.set_status(200)
        self.write({'candidates': [c.serialize() for c in candidates]})

    @tornado.web.authenticated
    def post(self, election_id):
        # get current user and check permissions
        user = self.current_user
        check_permissions(user)

        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('position', 'username', 'display_name')
        validate_parameters(body_json, required_parameters)
        validate_candidate(body_json, election_id)

        # create new candidate
        candidate = elections_model.Candidate()
        for parameter in required_parameters:
            setattr(candidate, parameter, body_json[parameter])
        setattr(candidate, 'election', str(election_id))
        elections_alchemy.add_or_update(candidate)

        # response
        self.set_status(201)
        self.write(candidate.serialize())


class SpecifiedCandidateHandler(BaseHandler):
    def get(self, election_id, candidate_id):
        # get candidate
        candidate = elections_alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))
        if candidate == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')

        # response
        self.set_status(200)
        self.write(candidate[0].serialize())

    @tornado.web.authenticated
    def put(self, election_id, candidate_id):
        # get current user and check permissions
        user = self.current_user
        check_permissions(user)

        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('id', 'election', 'position', 'username', 'display_name')
        validate_parameters(body_json, required_parameters)
        validate_candidate(body_json, election_id)

        # get election
        election = elections_alchemy.query_election(election_id=str(election_id))
        if election == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')

        # get candidate
        candidate = elections_alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))
        if candidate == list():
            raise exceptions.NotFound404Exception('candidate with specified ID not found')
        candidate = candidate[0]

        # update candidate
        for parameter in required_parameters:
            setattr(candidate, parameter, body_json[parameter])
        elections_alchemy.add_or_update(candidate)

        self.write(candidate.serialize())

    @tornado.web.authenticated
    def delete(self, election_id, candidate_id):
        # get current user and check permissions
        user = self.current_user
        check_permissions(user)

        # get candidate
        candidate = elections_alchemy.query_candidates(election_id=str(election_id), candidate_id=str(candidate_id))
        if candidate == list():
            raise exceptions.NotFound404Exception('candidate with specified ID not found')
        candidate = candidate[0]

        # get election
        election = elections_alchemy.query_election(election_id=str(election_id))
        if election == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')
        election = election[0]

        # dont allow deleting past candidates
        if election != elections_alchemy.query_current() and \
                election not in elections_alchemy.query_election(start=datetime.now()):
            raise exceptions.Forbidden403Exception('candidate not in the current election')

        # delete the candidate
        elections_alchemy.delete(candidate)

        # response
        self.set_status(204)
