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


class OperationNotFinished(DKGException):
    """
    Raised when requested operation result isn't ready.
    """

    pass


class OperationFailed(DKGException):
    """
    Raised when requested operation status is failed.
    """

    pass


class AccountMissing(DKGException):
    """
    Raised when trying to perform state-changing blockchain transaction without account specified.
    """

    pass


class InvalidAsset(DKGException):
    """
    Raised when root of the Merkle Tree built from N-Quads isn't the same as the assertionId.
    """

    pass


class LeafNotInTree(DKGException):
    """
    Raised when proof/verification requested for the leaf that is not the part of the Merkle Tree.
    """

    pass
