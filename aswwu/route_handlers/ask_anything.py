import json
import logging

import bleach
import tornado.web

from aswwu import BaseHandler

logger = logging.getLogger("aswwu")


class AskAnythingAddHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        ask_anything = AskAnything()
        ask_anything.question = bleach.clean(self.get_argument("question"))
        addOrUpdate(ask_anything)
        self.set_status(201)
        self.write({"status": "Question Submitted"})


class AskAnythingViewAllHandler(BaseHandler):
    def get(self):
        results = s.query(AskAnything).filter_by(authorized=True, reviewed=True)
        to_return = []
        user = self.get_current_user()
        if user:
            votes = s.query(AskAnythingVote).filter_by(voter=user.username).all()
            questions_voted = {}
            for vote in votes:
                questions_voted[vote.question_id] = True
        for question in results:
            serialized = question.serialize()
            serialized["has_voted"] = questions_voted.has_key(question.id) if user else False
            to_return.append(serialized)
        self.write(json.dumps(to_return))


class AskAnythingRejectedHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        if 'askanything' in user.roles or 'administrator' in user.roles:
            results = s.query(AskAnything).filter_by(authorized=False, reviewed=True)
            to_return = []
            for question in results:
                to_return.append(question.serialize())
            self.write(json.dumps(to_return))
        else:
            self.set_status(401)
            self.write({"status": "error", "reason": "Insufficient access"})


class AskAnythingVoteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, q_id):
        user = self.current_user
        votes = s.query(AskAnythingVote).filter_by(question_id=q_id, voter=user.username).all()
        # question = s.query(AskAnythingVote).filter_by(id=q_id).one()
        if len(votes) > 0:
            for vote in votes:
                delete_thing(vote)
            self.set_status(200)
            self.write({"Status": "Success. Vote Removed."})
        else:
            vote = AskAnythingVote()
            vote.question_id = q_id
            vote.voter = user.username
            addOrUpdate(vote)
            self.set_status(200)
            self.write({"status": "Success. Vote Added"})


class AskAnythingAuthorizeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        if 'askanything' in user.roles or 'administrator' in user.roles:
            results = s.query(AskAnything).filter_by(reviewed=False)
            to_return = []
            for question in results:
                to_return.append(question.serialize())
            self.write(json.dumps(to_return))
        else:
            self.set_status(401)
            self.write({"status": "error", "reason": "Insufficient access"})

    @tornado.web.authenticated
    def post(self, question_id):
        user = self.current_user
        authorized = self.get_argument("authorize").upper() == "Y"
        if 'askanything' in user.roles or 'administrator' in user.roles:
            ask_anything = query_by_field(AskAnything, id, question_id)
            ask_anything = s.query(AskAnything).filter_by(id=question_id).one()
            ask_anything.authorized = authorized
            ask_anything.reviewed = True
            addOrUpdate(ask_anything)
            self.set_status(200)
            self.write({"status": "Success"})
        else:
            self.set_status(401)
            self.write({"status": "error", "reason": "Insufficient access"})
