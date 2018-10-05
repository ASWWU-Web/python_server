import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Integer

from aswwu.models.bases import ElectionBase


class Vote(ElectionBase):
    wwuid = Column(String(7), ForeignKey('users.wwuid'), nullable=False)
    district = Column(String(50))
    vote_1 = Column(String(50))
    vote_2 = Column(String(50))
    write_in_1 = Column(String(50))
    write_in_2 = Column(String(50))
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    # return those who have voted
    def voters(self):
        return self.to_json(limitList=['wwuid'])

    def base_info(self):
        return self.to_json(limitList=['wwuid', 'updated_at'])


class Candidate(ElectionBase):
    username = Column(String(250), nullable=False)
    full_name = Column(String(250))
    district = Column(Integer)
