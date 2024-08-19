from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, Integer

from src.aswwu.models.bases import ElectionBase
import src.aswwu.alchemy_engines.mask as mask_alchemy


class Election(ElectionBase):
    __tablename__ = 'elections'

    election_type = Column(String(10))
    name = Column(String(100))
    max_votes = Column(Integer)
    start = Column(DateTime)
    end = Column(DateTime)
    show_results = Column(DateTime)

    def serialize(self):
        # determine if show_results field should be cast to a string
        if self.show_results is not None:
            show_results = datetime.strftime(self.show_results, '%Y-%m-%d %H:%M:%S.%f')
        else:
            show_results = None
        return {
            'id': self.id,
            'election_type': self.election_type,
            'name': self.name,
            'max_votes': self.max_votes,
            'start': datetime.strftime(self.start, '%Y-%m-%d %H:%M:%S.%f'),
            'end': datetime.strftime(self.end, '%Y-%m-%d %H:%M:%S.%f'),
            'show_results': show_results
        }


class Position(ElectionBase):
    __tablename__ = 'positions'

    position = Column(String(100))
    election_type = Column(String(10))
    active = Column(Boolean)
    order = Column(Integer)

    def serialize(self):
        return {
            'id': self.id,
            'position': self.position,
            'election_type': self.election_type,
            'active': self.active,
            'order': self.order
        }


class Vote(ElectionBase):
    __tablename__ = 'votes'

    election = Column(String(100), ForeignKey('elections.id'))
    position = Column(String(100), ForeignKey('positions.id'))
    vote = Column(String(100))
    username = Column(String(100))
    manual_entry = Column(String(100), default=None)

    def serialize(self):
        return {
            'id': self.id,
            'election': self.election,
            'position': self.position,
            'vote': self.vote,
            'username': self.username,
        }

    def serialize_ballot(self):
        student_id = mask_alchemy.query_by_username(self.username).wwuid
        return {
            'id': self.id,
            'election': self.election,
            'position': self.position,
            'vote': self.vote,
            'student_id': student_id,
            'manual_entry': self.manual_entry
        }


class Candidate(ElectionBase):
    __tablename__ = 'candidates'

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
