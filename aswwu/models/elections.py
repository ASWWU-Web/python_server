from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, Integer

from aswwu.models.bases import ElectionBase


class Election(ElectionBase):
    election_type = Column(String(10))
    start = Column(DateTime)
    end = Column(DateTime)
    show_results = Column(DateTime)
    name = Column(String(100))
    max_votes = Column(Integer)

    def serialize(self):
        # determine if show_results field should be cast to a string
        if self.show_results is not None:
            show_results = datetime.strftime(self.show_results, '%Y-%m-%d %H:%M:%S.%f')
        else:
            show_results = None
        return {
            'id': self.id,
            'election_type': self.election_type,
            'start': datetime.strftime(self.start, '%Y-%m-%d %H:%M:%S.%f'),
            'end': datetime.strftime(self.end, '%Y-%m-%d %H:%M:%S.%f'),
            'show_results': show_results,
            'name': self.name,
            'max_votes': self.max_votes
        }


class Position(ElectionBase):
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
