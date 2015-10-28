from sqlalchemy import Column, ForeignKey, Integer, String
from alchemy import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
