from sqlalchemy import Column, ForeignKey, String, DateTime, Integer, Boolean
from datetime import datetime

from aswwu.models.bases import ElectionBase
import aswwu.alchemy_new.elections as elections_alchemy
import aswwu.alchemy_new.mask as mask_alchemy
import aswwu.exceptions as exceptions


class Election(ElectionBase):
    election_type = Column(String(10))
    start = Column(DateTime)
    end = Column(DateTime)

    def serialize(self):
        return {
            'id': self.id,
            'election_type': self.election_type,
            'start': str(self.start),
            'end': str(self.end),
        }

    @staticmethod
    def validate(parameters):
        # check that election doesn't overlap with current or upcoming elections
        if elections_alchemy.detect_election_overlap(parameters["start"], parameters["end"]):
            raise exceptions.Forbidden403Exception('election takes place during another election')
        # checking that election doesn't start time in the past
        if elections_alchemy.detect_election_start(parameters["start"], parameters["end"]):
            raise exceptions.Forbidden403Exception('election takes place during the past')
        # check that end time isn't less than start time
        if elections_alchemy.detect_bad_end(parameters["start"], parameters["end"]):
            raise exceptions.Forbidden403Exception('start time is after end time')


class Position(ElectionBase):
    position = Column(String(100))
    election_type = Column(String(10))
    active = Column(Boolean)

    def serialize(self):
        return {
            'id': self.id,
            'position': self.position,
            'election_type': self.election_type,
            'active': self.active,
        }

    @staticmethod
    def validate(parameters):
        if not isinstance(parameters['active'], bool):
            raise exceptions.BadRequest400Exception('parameter active has type bool')


class Vote(ElectionBase):
    election = Column(String(100), ForeignKey('elections.id'))
    position = Column(String(100), ForeignKey('positions.id'))
    vote = Column(String(100))
    username = Column(String(100))

    def serialize(self):
        return {
            'id': self.id,
            'election': self.election,
            'position': self.position,
            'vote': self.vote,
            'username': self.username,
        }

    @staticmethod
    def validate(parameters, existing_vote=None):
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

        # check for duplicate votes
        if parameters['vote'] != getattr(existing_vote, 'vote', None) and \
                elections_alchemy.query_vote(election=specified_election[0].id,
                                             position=specified_position[0].id,
                                             vote=parameters['vote'],
                                             username=parameters['username']) != list():
            raise exceptions.Forbidden403Exception('you have already voted for this person')


class Candidate(ElectionBase):
    election = Column(String(100), ForeignKey('elections.id'))
    position = Column(String(100), ForeignKey('positions.id'))
    username = Column(String(100))
    display_name = Column(String(100))

    def serialize(self):
        return {
            'id': self.id,
            'election': self.election,
            'position': self.position,
            'username': self.username,
            'display_name': self.display_name,
        }

    @staticmethod
    def validate(parameters):
        # check to make sure there is an election to push candidates to
        election = elections_alchemy.query_election(election_id=parameters['election'])
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
        if not elections_alchemy.query_election(election_id=parameters['election']):
            raise exceptions.NotFound404Exception('election with specified ID not found')
