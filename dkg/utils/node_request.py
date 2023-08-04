# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Type

from dkg.dataclasses import HTTPRequestMethod
from dkg.exceptions import OperationFailed, OperationNotFinished
from dkg.types import UAL, Address, DataHexStr, NQuads


@dataclass
class NodeCall:
    method: HTTPRequestMethod
    path: str
    params: dict[str, Type] = field(default_factory=dict)
    data: dict[str, Type] | Type = field(default_factory=dict)


class NodeRequest:
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
    update = NodeCall(
        method=HTTPRequestMethod.POST,
        path="update",
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
        data={"id": UAL, "state": str, "hashFunctionId": int},
    )
    query = NodeCall(
        method=HTTPRequestMethod.POST,
        path="query",
        data={"query": str, "type": str, "repository": str},
    )


class LocalStoreOperationStatus(Enum):
    LOCAL_STORE_INIT_START = "LOCAL_STORE_INIT_START"
    LOCAL_STORE_INIT_END = "LOCAL_STORE_INIT_END"
    LOCAL_STORE_START = "LOCAL_STORE_START"
    LOCAL_STORE_END = "LOCAL_STORE_END"


class PublishOperationStatus(Enum):
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


class UpdateOperationStatus(Enum):
    UPDATE_START = "UPDATE_START"
    UPDATE_INIT_START = "UPDATE_INIT_START"
    UPDATE_INIT_END = "UPDATE_INIT_END"
    UPDATE_REPLICATE_START = "UPDATE_REPLICATE_START"
    UPDATE_REPLICATE_END = "UPDATE_REPLICATE_END"
    VALIDATING_UPDATE_ASSERTION_REMOTE_START = (
        "VALIDATING_UPDATE_ASSERTION_REMOTE_START"
    )
    VALIDATING_UPDATE_ASSERTION_REMOTE_END = "VALIDATING_UPDATE_ASSERTION_REMOTE_END"
    UPDATE_END = "UPDATE_END"


class StoreTypes(Enum):
    TRIPLE = "TRIPLE"
    PENDING = "PENDING"


class GetOperationStatus(Enum):
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
    QUERY_INIT_START = "QUERY_INIT_START"
    QUERY_INIT_END = "QUERY_INIT_END"
    QUERY_START = "QUERY_START"
    QUERY_END = "QUERY_END"


class OperationStatus(Enum):
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
    UPDATE = UpdateOperationStatus
    GET = GetOperationStatus
    QUERY = QueryOperationStatus


def validate_operation_status(operation_result: dict[str, Any]) -> None:
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
