# sheldon woodward
# jan 14, 2019

"""Custom exceptions for HTTP requests and other things."""

import logging
from tornado.web import HTTPError

from settings import config


logger = logging.getLogger(config["log_name"])


class BadRequest400Exception(HTTPError):
    """
    HTTP 400 error.
    """
    def __init__(self, log_message, *args, **kwargs):
        HTTPError.__init__(self, status_code=400, log_message=log_message, args=args, kwargs=kwargs)


class Unauthorized401Exception(HTTPError):
    """
    HTTP 401 error.
    """
    def __init__(self, log_message, *args, **kwargs):
        HTTPError.__init__(self, status_code=401, log_message=log_message, args=args, kwargs=kwargs)


class Forbidden403Exception(HTTPError):
    """
    HTTP 403 error.
    """
    def __init__(self, log_message, *args, **kwargs):
        HTTPError.__init__(self, status_code=403, log_message=log_message, args=args, kwargs=kwargs)


class NotFound404Exception(HTTPError):
    """
    HTTP 404 error.
    """
    def __init__(self, log_message, *args, **kwargs):
        HTTPError.__init__(self, status_code=404, log_message=log_message, args=args, kwargs=kwargs)


class Conflict409Exception(HTTPError):
    """
    HTTP 409 error.
    """
    def __init__(self, log_message, *args, **kwargs):
        HTTPError.__init__(self, status_code=409, log_message=log_message, args=args, kwargs=kwargs)


class InternalServerError500Exception(HTTPError):
    """
    HTTP 500 error.
    """
    def __init__(self, log_message, *args, **kwargs):
        HTTPError.__init__(self, status_code=500, log_message=log_message, args=args, kwargs=kwargs)
