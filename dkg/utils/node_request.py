from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Type

from dkg.dataclasses import HTTPRequestMethod
from dkg.exceptions import OperationFailed, OperationNotFinished
from dkg.types import UAL, Address, DataHexStr, NQuads


@dataclass
class NodeCall:
    """
    Represents a call to a node in the DKG system, including the method, path, and parameters.

    Attributes:
        method (HTTPRequestMethod): The HTTP request method for the call (e.g., GET, POST).
        path (str): The endpoint path for the call.
        params (dict[str, Type], optional): A dictionary of parameters for the call. Defaults
        to an empty dictionary.
        data (dict[str, Type] | Type, optional): Data to be sent with the call. Defaults to
        an empty dictionary.
    """

    method: HTTPRequestMethod
    path: str
    params: dict[str, Type] = field(default_factory=dict)
    data: dict[str, Type] | Type = field(default_factory=dict)


class NodeRequest:
    """
    A class containing predefined node calls for making requests to a node.

    Attributes:
        info (NodeCall): A node call to get information about the node.
        bid_suggestion (NodeCall): A node call to get a bid suggestion based on various
        parameters.
        get_operation_result (NodeCall): A node call to get the result of a specific operation.
        local_store (NodeCall): A node call to store data locally on the node.
        publish (NodeCall): A node call to publish an assertion to the blockchain.
        get (NodeCall): A node call to get the data of a specified Universal Asset Locator
        (UAL).
        query (NodeCall): A node call to execute a query against a specified repository.
    """

    info = NodeCall(method=HTTPRequestMethod.GET, path="info")
    bid_suggestion = NodeCall(
        method=HTTPRequestMethod.GET,
        path="bid-suggestion",
        params={
            "blockchain": str,
            "epochsNumber": int,
            "assertionSize": int,
            "contentAssetStorageAddress": Address,
            "firstAssertionId": DataHexStr,
            "hashFunctionId": int,
        },
    )
    get_operation_result = NodeCall(
        method=HTTPRequestMethod.GET,
        path="{operation}/{operation_id}",
    )

    local_store = NodeCall(
        method=HTTPRequestMethod.POST,
        path="local-store",
        data=list[dict[str, str | Address | NQuads]],
    )
    publish = NodeCall(
        method=HTTPRequestMethod.POST,
        path="publish",
        data={
            "assertionId": str,
            "assertion": NQuads,
            "blockchain": str,
            "contract": Address,
            "tokenId": int,
            "hashFunctionId": int,
        },
    )
    get = NodeCall(
        method=HTTPRequestMethod.POST,
        path="get",
        data={"id": UAL, "hashFunctionId": int},
    )
    query = NodeCall(
        method=HTTPRequestMethod.POST,
        path="query",
        data={"query": str, "type": str, "repository": str},
    )


class LocalStoreOperationStatus(Enum):
    """
    Enum representing the different statuses of a local store operation in the DKG system.
    """

    LOCAL_STORE_INIT_START = "LOCAL_STORE_INIT_START"
    LOCAL_STORE_INIT_END = "LOCAL_STORE_INIT_END"
    LOCAL_STORE_START = "LOCAL_STORE_START"
    LOCAL_STORE_END = "LOCAL_STORE_END"


class PublishOperationStatus(Enum):
    """
    Enum representing the different statuses of a publish operation in the DKG system.
    """

    VALIDATING_PUBLISH_ASSERTION_REMOTE_START = (
        "VALIDATING_PUBLISH_ASSERTION_REMOTE_START"
    )
    VALIDATING_PUBLISH_ASSERTION_REMOTE_END = "VALIDATING_PUBLISH_ASSERTION_REMOTE_END"
    INSERTING_ASSERTION = "INSERTING_ASSERTION"
    PUBLISHING_ASSERTION = "PUBLISHING_ASSERTION"
    PUBLISH_START = "PUBLISH_START"
    PUBLISH_INIT_START = "PUBLISH_INIT_START"
    PUBLISH_INIT_END = "PUBLISH_INIT_END"
    PUBLISH_LOCAL_STORE_START = "PUBLISH_LOCAL_STORE_START"
    PUBLISH_LOCAL_STORE_END = "PUBLISH_LOCAL_STORE_END"
    PUBLISH_REPLICATE_START = "PUBLISH_REPLICATE_START"
    PUBLISH_REPLICATE_END = "PUBLISH_REPLICATE_END"
    PUBLISH_END = "PUBLISH_END"


class StoreTypes(Enum):
    """
    Enum representing the different types of stores in the DKG system.
    """

    TRIPLE = "TRIPLE"
    PENDING = "PENDING"


class GetOperationStatus(Enum):
    """
    Enum representing the different statuses of a get operation in the DKG system.
    """

    ASSERTION_EXISTS_LOCAL_START = "ASSERTION_EXISTS_LOCAL_START"
    ASSERTION_EXISTS_LOCAL_END = "ASSERTION_EXISTS_LOCAL_END"
    GET_START = "GET_START"
    GET_INIT_START = "GET_INIT_START"
    GET_INIT_END = "GET_INIT_END"
    GET_LOCAL_START = "GET_LOCAL_START"
    GET_LOCAL_END = "GET_LOCAL_END"
    GET_REMOTE_START = "GET_REMOTE_START"
    GET_REMOTE_END = "GET_REMOTE_END"
    GET_FETCH_FROM_NODES_START = "GET_FETCH_FROM_NODES_START"
    GET_FETCH_FROM_NODES_END = "GET_FETCH_FROM_NODES_END"
    GET_END = "GET_END"


class QueryOperationStatus(Enum):
    """
    Enum representing the different statuses of a query operation in the DKG system.
    """

    QUERY_INIT_START = "QUERY_INIT_START"
    QUERY_INIT_END = "QUERY_INIT_END"
    QUERY_START = "QUERY_START"
    QUERY_END = "QUERY_END"


class OperationStatus(Enum):
    """
    Enum representing the different statuses of operations in the DKG system.
    """

    PENDING = "PENDING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    FIND_NODES_START = "FIND_NODES_START"
    FIND_NODES_END = "FIND_NODES_END"
    FIND_NODES_LOCAL_START = "FIND_NODES_LOCAL_START"
    FIND_NODES_LOCAL_END = "FIND_NODES_LOCAL_END"
    FIND_NODES_OPEN_CONNECTION_START = "FIND_NODES_OPEN_CONNECTION_START"
    FIND_NODES_OPEN_CONNECTION_END = "FIND_NODES_OPEN_CONNECTION_END"
    FIND_NODES_CREATE_STREAM_START = "FIND_NODES_CREATE_STREAM_START"
    FIND_NODES_CREATE_STREAM_END = "FIND_NODES_CREATE_STREAM_END"
    FIND_NODES_SEND_MESSAGE_START = "FIND_NODES_SEND_MESSAGE_START"
    FIND_NODES_SEND_MESSAGE_END = "FIND_NODES_SEND_MESSAGE_END"
    DIAL_PROTOCOL_START = "DIAL_PROTOCOL_START"
    DIAL_PROTOCOL_END = "DIAL_PROTOCOL_END"
    LOCAL_STORE = LocalStoreOperationStatus
    PUBLISH = PublishOperationStatus
    GET = GetOperationStatus
    QUERY = QueryOperationStatus


def validate_operation_status(operation_result: dict[str, Any]) -> None:
    """
    Validates the operation status of an operation in the DKG system.

    Args:
        operation_result (dict[str, Any]): The result of an operation in the DKG system.

    Raises:
        OperationNotFinished: If the operation isn't finished.
        OperationFailed: If the operation failed with an error.
    """
    try:
        status = OperationStatus(operation_result["status"])
    except ValueError:
        raise OperationNotFinished("Operation isn't finished")

    match status:
        case OperationStatus.COMPLETED:
            return
        case OperationStatus.FAILED:
            raise OperationFailed(
                f"Operation failed! {operation_result['data']['errorType']}: "
                f"{operation_result['data']['errorMessage']}."
            )
        case _:
            raise OperationNotFinished("Operation isn't finished")
