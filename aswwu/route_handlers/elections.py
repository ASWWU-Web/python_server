import tornado.web
import json

from datetime import datetime

from aswwu.base_handlers import BaseHandler
import aswwu.exceptions as exceptions
from aswwu.permissions import permission_and, admin_permission, elections_permission

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
    """
    List and create endpoints for votes.
    """

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
        if len(elections_alchemy.query_vote(election_id=specified_election[0].id,
                                            position_id=specified_position[0].id,
                                            username=str(user.username))) >= specified_election[0].max_votes:
            raise exceptions.Forbidden403Exception(
                'you may only cast {} vote/s'.format(str(specified_election[0].max_votes))
            )

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
    """
    Read and update endpoints for votes.
    """

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
        vote = elections_alchemy.query_vote(vote_id=vote_id, election_id=current_election.id,
                                            username=str(user.username))
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

    @tornado.web.authenticated
    @permission_and(elections_permission)
    def delete(self, vote_id):
        # get vote
        vote = elections_alchemy.query_vote(vote_id=str(vote_id))
        if vote == list():
            raise exceptions.NotFound404Exception('vote with specified ID not found')
        vote = vote[0]

        # get election
        election = elections_alchemy.query_election(election_id=str(vote.election))[0]

        # dont allow deleting past candidates
        if election != elections_alchemy.query_current():
            raise exceptions.Forbidden403Exception('vote not in the current election')

        # delete the vote
        elections_alchemy.delete(vote)

        # response
        self.set_status(204)


class ElectionHandler(BaseHandler):
    """
    List and create endpoints for elections.
    """

    def get(self):
        # build query parameter dict
        search_criteria = build_query_params(self.request.arguments)

        # get election
        elections = elections_alchemy.query_election(election_type=search_criteria.get('election_type', None),
                                                     name=search_criteria.get('name', None),
                                                     max_votes=search_criteria.get('max_votes', None),
                                                     start_before=search_criteria.get('start_before', None),
                                                     start_after=search_criteria.get('start_after', None),
                                                     end_before=search_criteria.get('end_before', None),
                                                     end_after=search_criteria.get('end_after', None))

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
        required_parameters = ('election_type', 'name', 'max_votes', 'start', 'end', 'show_results')
        elections_validator.validate_parameters(body_json, required_parameters)
        elections_validator.validate_election(body_json)

        # create new election
        election = elections_model.Election()
        for parameter in required_parameters:
            if parameter in ('start', 'end'):
                d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                setattr(election, parameter, d)
            elif parameter == 'show_results' and body_json[parameter] is not None:
                d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                setattr(election, parameter, d)
            else:
                setattr(election, parameter, body_json[parameter])
        elections_alchemy.add_or_update(election)

        # response
        self.set_status(201)
        self.write(election.serialize())


class SpecifiedElectionHandler(BaseHandler):
    """
    Read and update endpoints for elections.
    """

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
        required_parameters = ('id', 'election_type', 'name', 'max_votes', 'start', 'end', 'show_results')
        elections_validator.validate_parameters(body_json, required_parameters)
        elections_validator.validate_election(body_json, election)

        # update election
        for parameter in required_parameters:
            if parameter in ('start', 'end'):
                d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                setattr(election, parameter, d)
            elif parameter == 'show_results' and body_json[parameter] is not None:
                d = datetime.strptime(body_json[parameter], '%Y-%m-%d %H:%M:%S.%f')
                setattr(election, parameter, d)
            else:
                setattr(election, parameter, body_json[parameter])
        elections_alchemy.add_or_update(election)

        # response
        self.set_status(200)
        self.write(election.serialize())


class CurrentHandler(BaseHandler):
    """
    Read the current election.
    """

    def get(self):
        # get election
        election = elections_alchemy.query_current_or_upcoming()
        if election is None:
            raise exceptions.NotFound404Exception('there is no current or upcoming election')

        # response
        self.set_status(200)
        self.write(election.serialize())


class PositionHandler(BaseHandler):
    """
    List and create endpoints for positions.
    """

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
        required_parameters = ('position', 'election_type', 'active', 'order')
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
    """
    Read and update endpoints for positions.
    """

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
        required_parameters = ('id', 'position', 'election_type', 'active', 'order')
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
    """
    List and create endpoints for candidates.
    """

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
    """
    Read, update, and destroy endpoints for votes.
    """

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
        if election != elections_alchemy.query_current_or_upcoming():
            raise exceptions.Forbidden403Exception('candidate not in the current or upcoming election')

        # delete the candidate
        elections_alchemy.delete(candidate)

        # response
        self.set_status(204)


class VoteCountHandler(BaseHandler):
    """
    Read endpoint for counting votes.
    """

    def get(self, election_id):
        # get current user
        user = self.current_user

        # get election
        election = elections_alchemy.query_election(election_id=election_id)
        if election == list():
            raise exceptions.NotFound404Exception('election with specified ID not found')
        election = election[0]

        # check if results should not be sent
        is_admin = user is not None and (admin_permission in user.roles or elections_permission in user.roles)
        if not is_admin and (election.show_results is None or datetime.now() < election.show_results):
            raise exceptions.Forbidden403Exception('results are not available for this election')

        # count votes for each position
        position_totals = list()
        for position in elections_alchemy.query_position(election_type=election.election_type, active=True):
            # add each position to the totals
            position_summary = {
                'position': position.id,
                'votes': elections_alchemy.count_votes(election_id, position.id)
            }
            position_totals.append(position_summary)

        # response
        self.set_status(200)
        self.write({'positions': [position for position in position_totals]})
