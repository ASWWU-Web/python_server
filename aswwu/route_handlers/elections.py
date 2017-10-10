import logging

import tornado.web

from aswwu import BaseHandler

logger = logging.getLogger("aswwu")


# get all of the profiles in our database
class AllElectionVoteHandler(BaseHandler):
    def get(self):
        votes = query_all_Election(Election)
        self.write({'results': [v.info() for v in votes]})

# update user's vote
class ElectionVoteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, username):
        user = self.current_user
        if user.username == username or 'administrator' in user.roles:
            usrvote = query_by_wwuid_Election(Election, str(user.wwuid))
            # Fix this to be more efficient
            if len(usrvote) == 0:
                new_vote = Election(wwuid=str(user.wwuid))
                vote = addOrUpdateElection(new_vote)
            else:
                vote = election_s.query(Election).filter_by(wwuid=str(user.wwuid)).one()
            vote.candidate_one = self.get_argument('candidate_one','')
            vote.candidate_two = self.get_argument('candidate_two','')
            vote.sm_one = self.get_argument('sm_one','')
            vote.sm_two = self.get_argument('sm_two','')
            vote.new_department = self.get_argument('new_department','')
            vote.district = self.get_argument('district', '')

            addOrUpdateElection(vote)

            self.write({'vote': 'successfully voted'})
        else:
            self.write({'error': 'invalid voting permissions'})

class ElectionLiveFeedHandler(BaseHandler):
    def get(self):
        votes=query_all_Election(Election)
        self.write({'size': len(votes)})
