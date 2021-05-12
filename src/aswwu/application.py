import logging

import tornado.web
import tornado.options
import tornado.ioloop
import threading

from settings import keys
from src.aswwu import base_handlers as base
from src.aswwu.route_handlers import \
    mask, forms, pages, homepage, elections, \
    froala_images as froala


class Application(tornado.web.Application):
    handlers = [
        # base
        (r"/login", base.BaseLoginHandler),  # dummy route required by tornado
        (r"/verify", base.BaseVerifyLoginHandler),
        (r"/roles/(.*)", base.RoleHandler),
        # mask
        (r"/profile/(.*)/(.*)", mask.ProfileHandler),
        (r"/search/names", mask.SearchNamesFast),
        (r"/search/all", mask.SearchAllHandler),
        (r"/search/(.*)/(.*)", mask.SearchHandler),
        (r"/update/list_photos", mask.ListProfilePhotoHandler),
        (r"/update/list_pending_photos", mask.ListPendingProfilePhotoHandler),
        (r"/update/upload_photo", mask.UploadProfilePhotoHandler),
        (r"/update/upload_photo_direct", mask.DirectUploadProfilePhotoHandler),
        (r"/verify/mask-permissions", mask.VerifyMaskUploadPermissions),
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
        (r"/pages/media/approve/(.*)", froala.ApproveImageHandler),
        (r"/pages/media/dismay/(.*)", froala.DismayImageHandler),
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
            "secret_key": keys["hmac"]
        }
        self.options = tornado.options.options
        logger = logging.getLogger(tornado.options.options.log_name)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler("src/aswwu/"+tornado.options.options.log_name+".log")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("{'timestamp': %(asctime)s, 'loglevel' : %(levelname)s %(message)s }")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        tornado.web.Application.__init__(self, self.handlers, **settings)
        logger.info("Application started on port " + str(tornado.options.options.port))


def start_server():
    # https://stackoverflow.com/a/57688560
    application = Application()
    server = application.listen(tornado.options.options.port)
    event_loop_thread = threading.Thread(target=tornado.ioloop.IOLoop.current().start)
    event_loop_thread.daemon = True
    event_loop_thread.start()
    print 'The Tornado IOLoop thread has started.'
    return server, event_loop_thread, tornado.ioloop.IOLoop.current()


def stop_server(server, event_loop_thread, ioloop):
    server.stop()
    ioloop.stop()
    event_loop_thread.join()
