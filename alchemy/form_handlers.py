import tornado.web
import json
import logging
from alchemy.models import *
from alchemy.setup import *

from alchemy.base_handlers import BaseHandler

logger = logging.getLogger("aswwu")

class FormHandler(BaseHandler):
    def get(self, id):
        form = query_by_id(Form, id)
        if not form:
            return self.write({'error': 'no form exists with that ID'})
        questions = query_by_field(Question, "form_id", id)
        count = 0
        for q in questions:
            l = len(query_by_field(Answer, "question_id", q.id))
            if l > count: count = l
        for limit in form.limits.split(';'):
            kv = limit.split('=')
            if kv[0] == 'max':
                if kv[1] <= count:
                    questions = []
        self.write({'form': form.to_json(), 'questions': [q.to_json() for q in questions], 'submissions': count})

    @tornado.web.authenticated
    def put(self):
        title = self.get_argument("title", None)
        if not title:
            return self.write({'error': 'you must give the form a title'})
        limits = self.get_argument("limits", None)
        details = self.get_argument("details", None)
        administrators = self.current_user.wwuid
        form = Form(title=title, limits=limits, details=details, administrators=administrators)
        form = addOrUpdate(form)
        self.write({'form': form.to_json()})

    @tornado.web.authenticated
    def post(self, id):
        form = query_by_id(Form, id)
        if not form:
            return self.write({'error': 'no form exists with that ID'})
        wwuid = self.current_user.wwuid
        if wwuid not in [f.strip() for f in form.administrators.split(',')]:
            return self.write({'error': 'insufficient permissions'})
        title = self.get_argument("title", None)
        limits = self.get_argument("limits", None)
        details = self.get_argument("details", None)
        administrators = self.get_argument("administrators", None)
        form.title = title
        form.limits = limits
        form.details = details
        if administrators:
            form.administrators = administrators
        form = addOrUpdate(form)
        self.write({'form': form.to_json()})


class QuestionHandler(BaseHandler):
    def get(self, id):
        question = query_by_id(Question, id)
        if not question:
            return self.write({'error': 'no question exists with that ID'})
        answers = query_by_field(Answer, "question_id", id)
        user_answers = []
        for a in answers:
            if a.wwuid == self.current_user.wwuid:
                user_answers.append(a)
        self.write({'question': question.to_json(), 'answers': [a.to_json() for a in user_answers]})

    @tornado.web.authenticated
    def put(self, form_id):
        label = self.get_argument("label", None)
        form = query_by_id(Form, form_id)
        if not form or not label:
            return self.write({'error': 'you must give the question a label'})
        wwuid = self.current_user.wwuid
        if wwuid not in [f.strip() for f in form.administrators.split(',')]:
            return self.write({'error': 'insufficient permissions'})
        placeholder = self.get_argument("placeholder", None)
        type = self.get_argument("type", None)
        possible_values = self.get_argument("possible_values", None)
        limits = self.get_argument("limits", None)
        question = Question(form_id=form_id, label=label, placeholder=placeholder, type=type, possible_values=possible_values, limits=limits)
        question = addOrUpdate(question)
        self.write({'question': question.to_json()})

    @tornado.web.authenticated
    def post(self, id):
        question = query_by_id(Question, id)
        if not question:
            return self.write({'error': 'no question exists with that ID'})
        form = query_by_id(Form, question.form_id)
        if not form:
            return self.write({'error': 'no form matches this question'})
        wwuid = self.current_user.wwuid
        if wwuid not in [f.strip() for f in form.administrators.split(',')]:
            return self.write({'error': 'insufficient permissions'})
        label = self.get_argument("label", None)
        placeholder = self.get_argument("placeholder", None)
        type = self.get_argument("type", None)
        possible_values = self.get_argument("possible_values", None)
        limits = self.get_argument("limits", None)

        if label:
            question.label = label
        question.placeholder = placeholder
        question.type = type
        question.possible_values = possible_values
        question.limits = limits
        question = addOrUpdate(question)
        self.write({'question': question.to_json()})


class AnswerHandler(BaseHandler):
    def get(self, id):
        answer = query_by_id(Answer, id)
        if not answer:
            return self.write({'error': 'no answer exists with that ID'})
        self.write({'answer': answer.to_json()})

    @tornado.web.authenticated
    def put(self, question_id):
        wwuid = self.current_user.wwuid
        value = self.get_argument("value", None)
        question = query_by_id(Question, question_id)
        if not question or not value:
            return self.write({'error': 'you must give the answer a value'})
        if question.type in ["checkbox","radio","autocomplete"]:
            values = value.split(",")
            for v in values:
                if v.strip() not in [q.strip() for q in question.possible_values.split(",")]:
                    return self.write({'error': 'you must select a valid option for this question'})
        previous = s.query(Answer).filter_by(question_id=question_id).filter_by(wwuid=wwuid).all()
        if len(previous) > 0:
            answer = previous[0]
            answer.value = value
        else:
            answer = Answer(question_id=question_id, wwuid=wwuid, value=value)
        answer = addOrUpdate(answer)
        self.write({'answer': answer.to_json()})

    @tornado.web.authenticated
    def post(self, id):
        answer = query_by_id(Answer, id)
        if not answer:
            return self.write({'error': 'no answer exists with that ID'})
        wwuid = self.current_user.wwuid
        value = self.get_argument("value", None)
        question = query_by_id(Question, answer.question_id)
        if not question or not value:
            return self.write({'error': 'you must give the answer a value'})
        if question.type in ["checkbox","radio","autocomplete"]:
            if value not in [q.strip() for q in question.possible_values.split(",")]:
                return self.write({'error': 'you must select a valid option for this question'})
        answer.value = value
        answer = addOrUpdate(answer)
        self.write({'answer': answer.to_json()})

    @tornado.web.authenticated
    def delete(self, id):
        answer = query_by_id(Answer, id)
        if not answer:
            return self.write({'error': 'no answer exists with that ID'})
        wwuid = self.current_user.wwuid
        if answer.wwuid != wwuid:
            return self.write({'error': 'you do not have permission to delete that answer'})
        question = query_by_id(Question, answer.question_id)
        if not question:
            return self.write({'error': 'no question matches that answer'})
        delete_thing(answer)
        self.write(json.dumps('success'))

class FormAnswerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        form = query_by_id(Form, id)
        if not form:
            return self.write({'error': 'no form exists with that ID'})
        questions = query_by_field(Question, "form_id", id)
        answers = {}
        responders = []
        for q in questions:
            question_answers = []
            for answer in query_by_field(Answer, "question_id", q.id):
                wwuid = str(answer.wwuid)
                if wwuid not in answers:
                    answers[wwuid] = [wwuid]
                    responders.append([wwuid, answer.updated_at])
                answers[wwuid].append(str(answer.value))
        responders = sorted(responders, key=lambda x: x[1])
        responder_answers = []
        for resp in responders:
            responder_answers.append(answers[resp[0]])
        self.write({'form': form.to_json(), 'questions': [q.to_json() for q in questions], 'answers': responder_answers})


class ElectionFormHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        wwuid = self.current_user.wwuid
        vote = query_by_wwuid(ElectionVote, wwuid)
        if not vote:
            self.write({'vote': ''})
        else:
            self.write({'vote': vote[0].to_json()})

    @tornado.web.authenticated
    def post(self):
        wwuid = self.current_user.wwuid
        executive_vp = self.get_argument("executive_vp", None)
        social_vp = self.get_argument("social_vp", None)
        spiritual_vp = self.get_argument("spiritual_vp", None)
        president = self.get_argument("president", None)

        if not executive_vp or not social_vp or not spiritual_vp or not president:
            return self.write({'error': 'You must select at least one person for each position'})

        vote = query_by_wwuid(ElectionVote, wwuid)
        if not vote:
            vote = ElectionVote(wwuid=wwuid)
        else:
            vote = vote[0]
        vote.executive_vp = executive_vp
        vote.social_vp = social_vp
        vote.spiritual_vp = spiritual_vp
        vote.president = president

        vote = addOrUpdate(vote)
        self.write({'vote': vote.to_json()})
