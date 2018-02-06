# server.py

import logging

import tornado.autoreload
import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.options import define, options

import aswwu.base_handlers as base
import aswwu.route_handlers.ask_anything as ask_anything
import aswwu.route_handlers.elections as elections
import aswwu.route_handlers.forms as forms
import aswwu.route_handlers.instagram as instagram
import aswwu.route_handlers.mask as mask
import aswwu.route_handlers.saml as saml
import aswwu.route_handlers.volunteers as volunteers
import aswwu.route_handlers.pages as pages
# import our super secret keys
from settings import keys, testing

# import handlers as needed - here we import all of them

# define some initial options that can be passed in at run time
# e.g. `python server.py --port=8881` would run the server on port 8881
define("port", default=8888, help="run on the given port", type=int)
define("log_name", default="aswwu", help="name of the logfile")
define("current_year", default="1718")


# the main class that wraps everything up nice and neat
class Application(tornado.web.Application):
    def __init__(self):
        # define some global settings
        settings = {
            "login_url": "/login",
            "secret_key": keys["hmac"]
        }

        # list out the routes (as regex) and their corresponding handlers
        handlers = [
            (r"/login", base.BaseLoginHandler),
            (r"/profile/(.*)/(.*)", mask.ProfileHandler),
            (r"/profile_photo/(.*)/(.*)", mask.ProfilePhotoHandler),
            (r"/role/administrator", mask.AdministratorRoleHandler),
            (r"/role/volunteer", volunteers.VolunteerRoleHandler),
            (r"/search/all", mask.SearchAllHandler),
            (r"/search/(.*)/(.*)", mask.SearchHandler),
            (r"/update/(.*)", mask.ProfileUpdateHandler),
            (r"/volunteer", volunteers.VolunteerHandler),
            (r"/volunteer/(.*)", volunteers.VolunteerHandler),
            (r"/feed", instagram.FeedHandler),
            (r"/verify", base.BaseVerifyLoginHandler),
            (r"/", base.BaseIndexHandler),
            (r"/senate_election/showall", elections.AllElectionVoteHandler),
            (r"/senate_election/vote/(.*)", elections.ElectionVoteHandler),
            (r"/senate_election/livefeed", elections.ElectionLiveFeedHandler),
            (r"/saml/account/", saml.SamlHandler),
            (r"/matcher", mask.MatcherHandler),
            (r"/forms/job/new", forms.NewFormHandler),
            (r"/forms/job/view/(.*)", forms.ViewFormHandler),
            (r"/forms/job/delete", forms.DeleteFormHandler),
            (r"/forms/application/submit", forms.SubmitApplicationHandler),
            (r"/forms/application/view/(.*)/(.*)", forms.ViewApplicationHandler),
            (r"/forms/application/status", forms.ApplicationStatusHandler),
            (r"/forms/resume/upload", forms.ResumeUploadHandler),
            (r"/forms/resume/download/(.*)/(.*)", forms.ViewResumeHandler),
            (r"/askanything/add", ask_anything.AskAnythingAddHandler),
            (r"/askanything/view", ask_anything.AskAnythingViewAllHandler),
            (r"/askanything/view/rejected", ask_anything.AskAnythingRejectedHandler),
            (r"/askanything/(.*)/vote", ask_anything.AskAnythingVoteHandler),
            (r"/askanything/authorize", ask_anything.AskAnythingAuthorizeHandler),
            (r"/askanything/(.*)/authorize", ask_anything.AskAnythingAuthorizeHandler),
            (r"/pages", pages.GetAllHandler),
            (r"/pages/search/(.*)", pages.SearchHandler),
            (r"/pages/admin", pages.AdminAllHandler),
            (r"/pages/admin/(.*)/revision", pages.GetAllRevisionsHandler),
            (r"/pages/admin/(.*)/revision/(.*)", pages.SpecificRevisionHandler),
            (r"/pages/admin/(.*)", pages.AdminSpecificPageHandler),
            (r"/pages/(.*)", pages.GetHandler),
        ]

        # a bunch of setup stuff
        # mostly for logging and telling Tornado to start with the given settings
        self.options = options
        logger = logging.getLogger(options.log_name)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler("aswwu/"+options.log_name+".log")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("{'timestamp': %(asctime)s, 'loglevel' : %(levelname)s %(message)s }")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        tornado.web.Application.__init__(self, handlers, **settings)
        logger.info("Application started on port " + str(options.port))


# running `python server.py` actually tells python to rename this file as "__main__"
# hence this check to make sure we actually wanted to run the server
if __name__ == "__main__":
    # pass in the conf name with `python server.py CONF_NAME`
    # by default this is "default"
    config = tornado.options.parse_command_line()
    if len(config) == 0:
        conf_name = "default"
    else:
        conf_name = config[0]

    # initiate the IO loop for Tornado
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.options.parse_config_file("aswwu/"+conf_name+".conf")
    # create a new instance of our Application
    application = Application()
    application.listen(options.port)
    # tell it to autoreload if anything changes
    if testing['dev']:
        tornado.autoreload.start()
    io_loop.start()
