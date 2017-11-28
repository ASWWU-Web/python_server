# application.py

import logging

import tornado.autoreload
import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.options import define, options
import tornado.httpserver

import src.aswwu.base_handlers as base
import src.aswwu.route_handlers.ask_anything as ask_anything
import src.aswwu.route_handlers.elections as elections
import src.aswwu.route_handlers.forms as forms
import src.aswwu.route_handlers.instagram as instagram
import src.aswwu.route_handlers.mask as mask
import src.aswwu.route_handlers.saml as saml
import src.aswwu.route_handlers.volunteers as volunteers
# import our super secret keys
from settings import keys

# import handlers as needed - here we import all of them

# define some initial options that can be passed in at run time
# e.g. `python server.py --port=8881` would run the server on port 8881
define("port", default=8888, help="run on the given port", type=int)
define("log_name", default="aswwu", help="name of the logfile")
define("current_year", default="1718")


# the main class that wraps everything up nice and neat
class Application(tornado.web.Application):
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
        ]

    def __init__(self):
        # define some global settings
        settings = {
            "login_url": "/login",
            "secret_key": keys["hmac"]
        }

        # a bunch of setup stuff
        # mostly for logging and telling Tornado to start with the given settings
        self.options = options
        logger = logging.getLogger(options.log_name)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler("src/aswwu/"+options.log_name+".log")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("{'timestamp': %(asctime)s, 'loglevel' : %(levelname)s %(message)s }")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        tornado.web.Application.__init__(self, self.handlers, **settings)
        logger.info("Application started on port " + str(options.port))

def start_server(tornado, io_loop):
    # create a new instance of our Application
    global application
    application = Application()
    global server
    server = tornado.httpserver.HTTPServer(application)
    server.listen(options.port)
    # tell it to autoreload if anything changes
    tornado.autoreload.start()
    io_loop.start()
    print 'tornado server started'

def stop_server(io_loop):
    io_loop.add_callback(io_loop.stop)
    server.stop()
    print 'tornado server stopped'
