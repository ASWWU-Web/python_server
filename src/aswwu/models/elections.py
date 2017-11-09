import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

import src.aswwu.models.bases as base

ElectionBase = declarative_base(cls=base.ElectionBase)


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
