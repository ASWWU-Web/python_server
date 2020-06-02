# from sqlalchemy import Column, ForeignKey, String, Boolean
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
#
# import src.aswwu.models.bases as base
#
# Base = declarative_base(cls=base.Base)
#
#
# class AskAnything(Base):
#     question = Column(String(500), nullable=False)
#     reviewed = Column(Boolean, default=False)
#     authorized = Column(Boolean, default=False)
#     votes = relationship("AskAnythingVote", backref="askanything", lazy="joined")
#
#     def num_votes(self):
#         return len(self.votes)
#
#     def serialize(self):
#         return {'question_id': self.id, 'question': self.question, 'reviewed': self.reviewed,
#                 'authorized': self.authorized, 'votes': self.num_votes()}
#
#
# class AskAnythingVote(Base):
#     question_id = Column(String(50), ForeignKey('askanythings.id'))
#     voter = Column(String(75), nullable=False)
