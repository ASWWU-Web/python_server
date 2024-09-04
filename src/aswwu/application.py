import asyncio
import logging
from settings import config
import os
import signal


import tornado.web
from tornado.options import options

from src.aswwu import base_handlers as base
from src.aswwu.route_handlers import \
    mask, forms, pages, homepage, elections, \
    froala_images as froala

logger = logging.getLogger(config.logging.get('log_name'))


class Application(tornado.web.Application):
    handlers = [
        # base
        (r"/login", base.BaseLoginHandler),  # dummy route required by tornado
        (r"/logout", base.BaseLogoutHandler),
        (r"/verify", base.BaseVerifyLoginHandler),
        (r"/roles/(.*)", base.RoleHandler),
        (r"/healthcheck", base.HealthCheckHandler),
        # mask
        (r"/profile/(.*)/(.*)", mask.ProfileHandler),
        (r"/search/names", mask.SearchNamesFast),
        (r"/search/all", mask.SearchAllHandler),
        (r"/search/(.*)/(.*)", mask.SearchHandler),
        (r"/update/list_photos", mask.ListProfilePhotoHandler),
        (r"/update/list_pending_photos", mask.ListPendingProfilePhotoHandler),
        (r"/update/approve_photo/(.*)", mask.ApproveImageHandler),
        (r"/update/dismay_photo/(.*)", mask.DismayImageHandler),
        (r"/update/upload_photo", mask.UploadProfilePhotoHandler),
        (r"/update/(.*)", mask.ProfileUpdateHandler),
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
        settings = {
            "login_url": "/login",
            "secret_key": os.environ.get("HMAC_KEY"),
            "debug": os.environ.get("ENVIRONMENT") == "development"
        }
        self.options = tornado.options.options
        tornado.web.Application.__init__(self, self.handlers, **settings)
        logger.info("Application started on port " + str(tornado.options.options.port))

shutdown_event = asyncio.Event()

async def start_server():
    application = Application()
    application.listen(options.port)
    logging.getLogger(tornado.options.options.log_name).info("services running, press ctrl+c to stop")
    await shutdown_event.wait()

def stop_server(signum, frame):
    logging.getLogger(tornado.options.options.log_name).info("stopping services...")
    shutdown_event.set()
    exit(0)