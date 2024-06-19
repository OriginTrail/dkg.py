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
from enum import auto, Enum
from typing import Any, Type

from dkg.dataclasses import BidSuggestionRange, HTTPRequestMethod
from dkg.exceptions import OperationFailed, OperationNotFinished
from dkg.types import  AutoStrEnumUpperCase, UAL, Address, DataHexStr, NQuads


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
            "bidSuggestionRange": BidSuggestionRange,
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


class LocalStoreOperationStatus(AutoStrEnumUpperCase):
    LOCAL_STORE_INIT_START = auto()
    LOCAL_STORE_INIT_END = auto()
    LOCAL_STORE_START = auto()
    LOCAL_STORE_END = auto()


class PublishOperationStatus(Enum):
    VALIDATING_PUBLISH_ASSERTION_REMOTE_START = auto()
    VALIDATING_PUBLISH_ASSERTION_REMOTE_END = auto()
    INSERTING_ASSERTION = auto()
    PUBLISHING_ASSERTION = auto()
    PUBLISH_START = auto()
    PUBLISH_INIT_START = auto()
    PUBLISH_INIT_END = auto()
    PUBLISH_LOCAL_STORE_START = auto()
    PUBLISH_LOCAL_STORE_END = auto()
    PUBLISH_REPLICATE_START = auto()
    PUBLISH_REPLICATE_END = auto()
    PUBLISH_END = auto()


class UpdateOperationStatus(AutoStrEnumUpperCase):
    UPDATE_START = auto()
    UPDATE_INIT_START = auto()
    UPDATE_INIT_END = auto()
    UPDATE_REPLICATE_START = auto()
    UPDATE_REPLICATE_END = auto()
    VALIDATING_UPDATE_ASSERTION_REMOTE_START = auto()
    VALIDATING_UPDATE_ASSERTION_REMOTE_END = auto()
    UPDATE_END = auto()


class StoreTypes(AutoStrEnumUpperCase):
    TRIPLE = auto()
    PENDING = auto()


class GetOperationStatus(AutoStrEnumUpperCase):
    ASSERTION_EXISTS_LOCAL_START = auto()
    ASSERTION_EXISTS_LOCAL_END = auto()
    GET_START = auto()
    GET_INIT_START = auto()
    GET_INIT_END = auto()
    GET_LOCAL_START = auto()
    GET_LOCAL_END = auto()
    GET_REMOTE_START = auto()
    GET_REMOTE_END = auto()
    GET_FETCH_FROM_NODES_START = auto()
    GET_FETCH_FROM_NODES_END = auto()
    GET_END = auto()


class QueryOperationStatus(AutoStrEnumUpperCase):
    QUERY_INIT_START = auto()
    QUERY_INIT_END = auto()
    QUERY_START = auto()
    QUERY_END = auto()


class OperationStatus(AutoStrEnumUpperCase):
    PENDING = auto()
    FAILED = auto()
    COMPLETED = auto()
    FIND_NODES_START = auto()
    FIND_NODES_END = auto()
    FIND_NODES_LOCAL_START = auto()
    FIND_NODES_LOCAL_END = auto()
    FIND_NODES_OPEN_CONNECTION_START = auto()
    FIND_NODES_OPEN_CONNECTION_END = auto()
    FIND_NODES_CREATE_STREAM_START = auto()
    FIND_NODES_CREATE_STREAM_END = auto()
    FIND_NODES_SEND_MESSAGE_START = auto()
    FIND_NODES_SEND_MESSAGE_END = auto()
    DIAL_PROTOCOL_START = auto()
    DIAL_PROTOCOL_END = auto()
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
