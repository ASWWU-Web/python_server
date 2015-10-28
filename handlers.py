import tornado.web
import logging
from alchemy import *

logger = logging.getLogger("pyserver")


class BaseHandler(tornado.web.RequestHandler):
    def tester(self):
        return True


class IndexHandler(BaseHandler):
    def get(self):
        logger.debug("blah")
        s = dbs()
        s.add(User(name='test'))
        s.commit()
        self.write("testing")
