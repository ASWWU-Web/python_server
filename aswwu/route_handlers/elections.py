import tornado.web
import json

from datetime import datetime

from aswwu.base_handlers import BaseHandler
import aswwu.exceptions as exceptions
from aswwu.permissions import permission_and, elections_permission

import aswwu.alchemy_new.elections as elections_alchemy
import aswwu.models.elections as elections_model
import aswwu.validators.elections as elections_validator


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
        votes = elections_alchemy.query_vote(election_id=current_election.id,
                                             username=str(user.username),
                                             position_id=search_criteria.get('position', None),
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
        elections_validator.validate_parameters(body_json, required_parameters)
        body_json['username'] = str(user.username)
        elections_validator.validate_vote(body_json)

        # check for too many votes
        specified_election = elections_alchemy.query_election(election_id=body_json['election'])
        specified_position = elections_alchemy.query_position(position_id=body_json['position'])
        if specified_election[0].election_type == 'aswwu' and \
                len(elections_alchemy.query_vote(election_id=specified_election[0].id,
                                                 position_id=specified_position[0].id,
                                                 username=str(user.username))) >= 1:
            raise exceptions.Forbidden403Exception('you can only vote for one aswwu representative')
        elif specified_election[0].election_type == 'senate' and \
                len(elections_alchemy.query_vote(election_id=specified_election[0].id,
                                                 position_id=specified_position[0].id,
                                                 username=str(user.username))) >= 2:
            raise exceptions.Forbidden403Exception('you can only vote for two senators')

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
                                            election_id=current_election.id,
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
        vote = elections_alchemy.query_vote(vote_id=vote_id, election_id=current_election.id, username=str(user.username))
        if vote == list():
            raise exceptions.NotFound404Exception('vote with specified ID not found')
        vote = vote[0]

        # validate parameters
        required_parameters = ('id', 'election', 'position', 'vote', 'username')
        elections_validator.validate_parameters(body_json, required_parameters)
        body_json['username'] = str(user.username)
        elections_validator.validate_vote(body_json, vote)

        # update vote
        for parameter in required_parameters:
            if parameter not in ('id', 'username'):
                setattr(vote, parameter, body_json[parameter])
        setattr(vote, 'username', str(user.username))
        elections_alchemy.add_or_update(vote)

        # response
        self.set_status(200)
        self.write(vote.serialize())


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
    @permission_and(elections_permission)
    def post(self):
        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('election_type', 'start', 'end')
        elections_validator.validate_parameters(body_json, required_parameters)
        elections_validator.validate_election(body_json)

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
        election = election[0]

        # response
        self.set_status(200)
        self.write(election.serialize())

    @tornado.web.authenticated
    @permission_and(elections_permission)
    def put(self, election_id):
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
        elections_validator.validate_parameters(body_json, required_parameters)
        elections_validator.validate_election(body_json)

        # update election
        for parameter in required_parameters:
            if parameter in ("start", "end"):
                d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                setattr(election, parameter, d)
            else:
                setattr(election, parameter, body_json[parameter])
        elections_alchemy.add_or_update(election)

        # response
        self.set_status(200)
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
    @permission_and(elections_permission)
    def post(self):
        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('position', 'election_type', 'active')
        elections_validator.validate_parameters(body_json, required_parameters)
        elections_validator.validate_position(body_json)

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
    @permission_and(elections_permission)
    def put(self, position_id):
        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('id', 'position', 'election_type', 'active')
        elections_validator.validate_parameters(body_json, required_parameters)
        elections_validator.validate_position(body_json)

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
                                                        position_id=search_criteria.get('position', None),
                                                        username=search_criteria.get('username', None),
                                                        display_name=search_criteria.get('display_name', None))

        # response
        self.set_status(200)
        self.write({'candidates': [c.serialize() for c in candidates]})

    @tornado.web.authenticated
    @permission_and(elections_permission)
    def post(self, election_id):
        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('position', 'username', 'display_name')
        elections_validator.validate_parameters(body_json, required_parameters)
        body_json['election'] = election_id
        elections_validator.validate_candidate(body_json)

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
    @permission_and(elections_permission)
    def put(self, election_id, candidate_id):
        # load request body
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)

        # validate parameters
        required_parameters = ('id', 'election', 'position', 'username', 'display_name')
        elections_validator.validate_parameters(body_json, required_parameters)
        body_json['election'] = election_id
        elections_validator.validate_candidate(body_json)

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

        # response
        self.set_status(200)
        self.write(candidate.serialize())

    @tornado.web.authenticated
    @permission_and(elections_permission)
    def delete(self, election_id, candidate_id):
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
