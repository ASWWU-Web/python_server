import logging
from alchemy.base_handlers import BaseHandler

logger = logging.getLogger("aswwu")

class LookUpOldHandler(BaseHandler):
    def get(self, table):
        things = query_old_all(table)
        for thing in things:
            self.write(str(thing.id))

    def post(self):
        users = query_old_all('users')
        profiles = query_old_all('profiles')
        volunteers = query_old_all('volunteers')

        for u in users:
            new_user = User(wwuid=u.wwuid, username=u.username, full_name=u.fullname, status=u.status, roles=u.roles)
            addOrUpdate(new_user)
