import logging

import tornado.web
from tornado.options import options

from settings import keys
from src.aswwu import base_handlers as base
from src.aswwu.route_handlers import \
    mask, volunteers, instagram, forms, pages, homepage, elections, \
    froala_images as froala


class Application(tornado.web.Application):
    # list out the routes (as regex) and their corresponding handlers
    handlers = [
        # base
        (r"/login", base.BaseLoginHandler),  # dummy route required by tornado
        (r"/verify", base.BaseVerifyLoginHandler),
        # mask
        (r"/profile/(.*)/(.*)", mask.ProfileHandler),
        (r"/profile_photo/(.*)/(.*)", mask.ProfilePhotoHandler),  # UNUSED
        (r"/role/administrator", mask.AdministratorRoleHandler),  # UNUSED
        (r"/role/volunteer", volunteers.VolunteerRoleHandler),  # UNUSED
        (r"/search/names", mask.SearchNamesFast),
        (r"/search/all", mask.SearchAllHandler),
        (r"/search/(.*)/(.*)", mask.SearchHandler),
        (r"/update/list_photos", mask.ListProfilePhotoHandler),
        (r"/update/(.*)", mask.ProfileUpdateHandler),
        (r"/volunteer", volunteers.VolunteerHandler),  # UNUSED
        (r"/volunteer/(.*)", volunteers.VolunteerHandler),  # UNUSED
        (r"/feed", instagram.FeedHandler),  # UNUSED
        (r"/matcher", mask.MatcherHandler),  # UNUSED
        # jobs
        (r"/forms/job/new", forms.NewFormHandler),
        (r"/forms/job/view/(.*)", forms.ViewFormHandler),
        (r"/forms/job/delete", forms.DeleteFormHandler),
        (r"/forms/job/edit/(.*)", forms.EditFormHandler),
        (r"/forms/application/submit", forms.SubmitApplicationHandler),
        (r"/forms/application/view/(.*)/(.*)", forms.ViewApplicationHandler),
        (r"/forms/application/status", forms.ApplicationStatusHandler),
        (r"/forms/resume/upload", forms.ResumeUploadHandler),
        (r"/forms/resume/download/(.*)/(.*)", forms.ViewResumeHandler),
        (r"/forms/application/export/(.*)", forms.ExportApplicationsHandler),
        # pages
        (r"/pages", pages.GetAllHandler),
        (r"/pages/search", pages.SearchHandler),
        (r"/pages/categories", pages.CategoryHandler),
        (r"/pages/departments", pages.DepartmentHandler),
        (r"/pages/featureds", pages.FeaturedsHandler),
        (r"/pages/featureds/(.*)", pages.AdminFeaturedsHandler),
        (r"/pages/tags", pages.TagsHandler),
        (r"/pages/admin", pages.AdminAllHandler),
        (r"/pages/admin/(.*)/revision", pages.GetAllRevisionsHandler),
        (r"/pages/admin/(.*)/revision/(.*)", pages.SpecificRevisionHandler),
        (r"/pages/admin/(.*)", pages.AdminSpecificPageHandler),
        (r"/pages/media/upload_image", froala.UploadHandler),
        (r"/pages/media/load_images", froala.LoadAllHandler),
        (r"/pages/media/static/(.*)", froala.LoadImageHandler),
        (r"/pages/(.*)", pages.GetHandler),
        # homepage
        (r"/homepage/open_forum", homepage.OpenForumHandler),
        # elections
        (r"/elections/vote", elections.VoteHandler),
        (r"/elections/vote/(.*)", elections.SpecificVoteHandler),
        (r"/elections/election/(.*)/ballot", elections.BallotHandler),
        (r"/elections/election/(.*)/ballot/(.*)", elections.SpecifiedBallotHandler),
        (r"/elections/election/(.*)/candidate", elections.CandidateHandler),
        (r"/elections/election/(.*)/candidate/(.*)", elections.SpecifiedCandidateHandler),
        (r"/elections/position", elections.PositionHandler),
        (r"/elections/position/(.*)", elections.SpecifiedPositionHandler),
        (r"/elections/election", elections.ElectionHandler),
        (r"/elections/election/(.*)/count", elections.VoteCountHandler),
        (r"/elections/election/(.*)", elections.SpecifiedElectionHandler),
        (r"/elections/current", elections.CurrentHandler),
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
        # see https://stackoverflow.com/a/11315061 for notation
        tornado.web.Application.__init__(self, self.handlers, **settings)
        logger.info("Application started on port " + str(options.port))