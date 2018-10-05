import logging

import tornado.web
import json

from aswwu.base_handlers import BaseHandler
import aswwu.alchemy as alchemy
import aswwu.models.elections as election_model

logger = logging.getLogger("aswwu")

election_db = alchemy.election_db


# update user's vote
class ElectionVoteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, username):
        user = self.current_user
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)
        vote = alchemy.query_vote_election(str(user.wwuid))
        # Fix this to be more efficient
        if len(vote) == 0:
            new_vote = election_model.Vote(wwuid=str(user.wwuid))
        else:
            new_vote = election_db.query(election_model.Vote).filter_by(wwuid=str(user.wwuid)).one()

        new_vote.district = str(body_json['district'])
        new_vote.vote_1 = str(body_json['vote_1'])
        new_vote.vote_2 = str(body_json['vote_2'])
        new_vote.write_in_1 = str(body_json['write_in_1'])
        new_vote.write_in_2 = str(body_json['write_in_2'])

        alchemy.add_or_update_election(vote)

        self.write({'vote': 'successfully voted'})


class ElectionCandidateHandler(BaseHandler):
    def get(self, district):
        candidates = alchemy.query_district_election(district)
        self.write({
            'candidates': [c.to_json for c in candidates]
        })

    @tornado.web.authenticated
    def post(self, district):
        # variables
        user = self.current_user
        body = self.request.body.decode('utf-8')
        body_json = json.loads(body)
        # check authorization
        if 'election-admin' not in user.roles and 'administrator' not in user.roles:
            self.set_status(403)
            self.write({'status': 'insufficient permissions'})
        candidate = alchemy.query_candidate_election(str(body_json['username']))
        # Fix this to be more efficient
        if len(candidate) == 0:
            new_candidate = election_model.Candidate(username=str(body_json['username']))
        else:
            new_candidate = alchemy.query_candidate_election(username=str(body_json['username']))

        new_candidate.full_name = str(body_json['full_name'])
        new_candidate.district = str(district)

        alchemy.add_or_update_election(new_candidate)

        self.write({'candidate': 'successfully modified/created'})

