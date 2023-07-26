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


class NetworkNotSupported(DKGException):
    """
    Raised when blockchain provider is initialized for unsupported network.
    """

    pass


class InvalidStateOption(DKGException):
    """
    Raised when invalid state option given to the get operation.
    """

    pass


class MissingKnowledgeAssetState(DKGException):
    """
    Raised when search for the Knowledge Asset state on the network has failed.
    """

    pass


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
    Raised when trying to perform state-changing blockchain transaction without account
    specified.
    """

    pass


class InvalidDataset(DKGException):
    """
    Raised when dataset URDNA2015 normalization doesn't result in any quads.
    """

    pass


class DatasetInputFormatNotSupported(DKGException):
    """
    Raised when trying to normalize RDF dataset with not supported input format.
    """

    pass


class DatasetOutputFormatNotSupported(DKGException):
    """
    Raised when trying to convert RDF dataset to not supported output format.
    """

    pass


class InvalidKnowledgeAsset(DKGException):
    """
    Raised when root of the Merkle Tree built from N-Quads isn't the same as the
    assertionId.
    """

    pass


class InvalidTokenAmount(DKGException):
    """
    Raised when token amount for operation isn't specified and suggested amount is less
    or equal to what is already present in the contract.
    """

    pass


class LeafNotInTree(DKGException):
    """
    Raised when proof/verification requested for the leaf that is not the part of the
    Merkle Tree.
    """

    pass
