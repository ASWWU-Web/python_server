# sheldon woodward
# jan 14, 2019

"""Custom exceptions for HTTP requests and other things."""


class HTTPException(Exception):
    """
    Generic HTTPException.
    """
    def __init__(self, *args):
        Exception.__init__(self, *args)


class BadRequest400Exception(HTTPException):
    """
    HTTP 400 error.
    """
    def __init__(self, *args):
        HTTPException.__init__(self, *args)


class Unauthorized401Exception(HTTPException):
    """
    HTTP 401 error.
    """
    def __init__(self, *args):
        HTTPException.__init__(self, *args)


class Forbidden403Exception(HTTPException):
    """
    HTTP 403 error.
    """
    def __init__(self, *args):
        HTTPException.__init__(self, *args)


class NotFound404Exception(HTTPException):
    """
    HTTP 404 error.
    """
    def __init__(self, *args):
        HTTPException.__init__(self, *args)


class Conflict409Exception(HTTPException):
    """
    HTTP 409 error.
    """
    def __init__(self, *args):
        HTTPException.__init__(self, *args)


class InternalServerError500Exception(HTTPException):
    """
    HTTP 500 error.
    """
    def __init__(self, *args):
        HTTPException.__init__(self, *args)
