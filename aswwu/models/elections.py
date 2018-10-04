import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Integer

from aswwu.models.bases import ElectionBase


class User(ElectionBase):
    wwuid = Column(String(7), unique=True)
    username = Column(String(250), nullable=False)
    full_name = Column(String(250))
    status = Column(String(250))
    roles = Column(String(500))


class Election(ElectionBase):
    wwuid = Column(String(7), ForeignKey('users.wwuid'), nullable=False)
    candidate_one = Column(String(50))
    candidate_two = Column(String(50))
    sm_one = Column(String(50))
    sm_two = Column(String(50))
    new_department = Column(String(150))
    district = Column(String(50))
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    # return those who have voted
    def voters(self):
        return self.to_json(limitList=['wwuid'])

    def base_info(self):
        return self.to_json(limitList=['wwuid', 'updated_at'])

    def info(self):
        return self.to_json(limitList=['wwuid', 'candidate_one', 'candidate_two', 'sm_one', 'sm_two',
                                       'new_department', 'updated_at'])


class Candidate(ElectionBase):
    username = Column(String(250), nullable=False)
    full_name = Column(String(250))
    district = Column(Integer)
