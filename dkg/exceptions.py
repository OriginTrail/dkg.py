class DKGException(Exception):
    """
    Exception mixin inherited by all exceptions of dkg.py
    This allows::
        try:
            some_call()
        except DKGException:
            # deal with dkg exception
        except:
            # deal with other exceptions
    """


class ValidationError(DKGException):
    """
    Raised when something does not pass a validation check.
    """

    pass


class InvalidRequest(DKGException):
    """
    Raised by a manager to signal that blockchain/node request method
    doesn't exist.
    """

    pass


class HTTPRequestMethodNotSupported(DKGException):
    """
    Raised if used HTTP method isn't supported
    """

    pass


class NodeRequestError(DKGException):
    """
    Raised by Node HTTP Provider if error occured during request.
    """

    pass
