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
        self.write({'form': form.to_json(), 'questions': [q.to_json() for q in questions]})

    @tornado.web.authenticated
    def put(self):
        title = self.get_argument("title", None)
        if not title:
            return self.write({'error': 'you must give the form a title'})
        limits = self.get_argument("limits", None)
        administrators = self.current_user.wwuid
        form = Form(title=title, limits=limits, administrators=administrators)
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
        administrators = self.get_argument("administrators", None)
        if title:
            form.title = title
        if limits:
            form.limits = limits
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
        self.write({'question': question.to_json(), 'answers': [a.to_json() for a in answers]})

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
