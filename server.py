
import os
import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.options import define, options

from alchemy.base_handlers import *
from alchemy.search_handlers import *

from alchemy.form_handlers import *
from alchemy.role_handlers import *
from alchemy.volunteer_handlers import *

# from alchemy.old_db_handlers import *

define("port", default=8888, help="run on the given port", type=int)
define("log_name", default="aswwu", help="name of the logfile")
define("auth_url", default="https://aswwu.com/auth")
define("current_year", default="1516")


class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            "login_url": "/login",
            "secret_key": "qtB91kGZF0ysv39GLaA5a6fVK7TnE6d5"
        }

        handlers = [
            # (r"/answer", AnswerHandler),
            # (r"/answer/(.*)", AnswerHandler),
            # (r"/collegian_search/(.*)", CollegianArticleSearch),
            # (r"/election", ElectionFormHandler),
            # (r"/form", FormHandler),
            # (r"/form/(.*)", FormHandler),
            # (r"/form_answers/(.*)", FormAnswerHandler),
            (r"/login", LoginHandler),
            # (r"/old_db", LookUpOldHandler),
            (r"/profile/(.*)/(.*)", ProfileHandler),
            (r"/profile_photo/(.*)/(.*)", ProfilePhotoHandler),
            # (r"/question", QuestionHandler),
            # (r"/question/(.*)", QuestionHandler),
            (r"/role/administrator", AdministratorRoleHandler),
            # (r"/role/collegian", CollegianRoleHandler),
            (r"/role/volunteer", VolunteerRoleHandler),
            (r"/search/all", ListProfilesHandler),
            (r"/search/(.*)/(.*)", SearchHandler),
            (r"/townathlon_form", TownathlonFormHandler),
            (r"/update/(.*)", UpdateProfileHandler),
            (r"/volunteer", VolunteerHandler),
            (r"/volunteer/(.*)", VolunteerHandler),
            (r"/verify", VerifyLoginHandler),
            (r"/", IndexHandler),
        ]

        self.options = options
        logger = logging.getLogger(options.log_name)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler("etc/"+options.log_name+".log")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("{'timestamp': %(asctime)s, 'loglevel' : %(levelname)s %(message)s }")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        tornado.web.Application.__init__(self, handlers, **settings)
        logger.info("Application started on port " + str(options.port))


if __name__ == "__main__":
    config = tornado.options.parse_command_line()
    if len(config) == 0:
        conf_name = "default"
    else:
        conf_name = config[0]
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.options.parse_config_file("etc/"+conf_name+".conf")
    application = Application()
    application.listen(options.port)
    tornado.autoreload.start()
    io_loop.start()
