from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from aswwu.models.bases import JobsBase


class JobForm(JobsBase):
    job_name = Column(String(100), nullable=False)
    job_description = Column(String(10000))
    department = Column(String(150))
    visibility = Column(Boolean, default=False)
    owner = Column(String(100), nullable=False)
    questions = relationship("JobQuestion", backref="jobforms", lazy="joined")
    image = Column(String(100), nullable=False)

    def serialize(self):
        questions = []
        for question in self.questions:
            questions.append(question.serialize())
        return {'job_name': self.job_name, 'job_description': self.job_description,
                'visibility': self.visibility, 'owner': self.owner, 'department': self.department,
                'image': self.image, 'questions': questions, 'jobID': self.id}

    def min(self):
        return {'job_name': self.job_name, 'job_description': self.job_description,
                'department': self.department, 'image': self.image, 'jobID': self.id,
                'visibility': self.visibility, 'owner': self.owner}


class JobQuestion(JobsBase):
    question = Column(String(5000))
    jobID = Column(String(50), ForeignKey('jobforms.id'))

    def serialize(self):
        return {'question': self.question, 'id': self.id}


class JobApplication(JobsBase):
    jobID = Column(String(50), ForeignKey('jobforms.id'))
    answers = relationship("JobAnswer", backref="jobapplications", lazy="joined")
    username = Column(String(100), nullable=False)
    status = Column(String(50))

    def serialize(self):
        answers = []
        for answer in self.answers:
            answers.append(answer.serialize())
        return {'jobID': self.jobID, 'answers': answers,
                'username': self.username, 'status': self.status}

    def min(self):
        return {'jobID': self.jobID, 'username': self.username,
                'status': self.status}


class JobAnswer(JobsBase):
    questionID = Column(String(50), ForeignKey('jobquestions.id'))
    answer = Column(String(10000))
    applicationID = Column(String(50), ForeignKey('jobapplications.id'))

    def serialize(self):
        return {'questionID': self.questionID, 'answer': self.answer}
