from sqlalchemy import Column, ForeignKey, String, DateTime, Integer, Boolean

from aswwu.models.bases import ElectionBase


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
            'vote':     self.vote,
            'username': self.username,
        }


class Candidate(ElectionBase):
    election = Column(String(100), ForeignKey('elections.id'))
    position = Column(String(100), ForeignKey('positions.id'))
    username = Column(String(100))
    display_name = Column(String(100))

    def serialize(self):
        return{
            'id':           self.id,
            'election':     self.election,
            'position':     self.position,
            'username':     self.username,
            'display_name': self.display_name

        }