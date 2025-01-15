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
from dkg.types import AutoStrEnumUpperCase, UAL, Address, DataHexStr

import time


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

    publish = NodeCall(
        method=HTTPRequestMethod.POST,
        path="publish",
        data={
            "datasetRoot": str,
            "dataset": dict[str, list[str]],
            "blockchain": str,
            "hashFunctionId": int,
            "minimumNumberOfNodeReplications": int,
        },
    )

    finality_status = NodeCall(
        method=HTTPRequestMethod.GET,
        path="finality",
        params={"ual": UAL},
    )

    finality = NodeCall(
        method=HTTPRequestMethod.GET,
        path="ask",
        params={"ual": UAL},
    )

    get = NodeCall(
        method=HTTPRequestMethod.POST,
        path="get",
        data={
            "id": UAL,
            "contentType": str,
            "includeMetadata": bool,
            "hashFunctionId": int,
            "paranetUAL": UAL,
            "subjectUAL": UAL,
        },
    )
    query = NodeCall(
        method=HTTPRequestMethod.POST,
        path="query",
        data={
            "query": str,
            "type": str,
            "repository": str | None,
            "paranet_ual": str | None,
        },
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


class StoreTypes(AutoStrEnumUpperCase):
    TRIPLE = auto()
    TRIPLE_PARANET = auto()
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


def finality_status(
        ual: str,
        required_confirmations: int,
        max_number_of_retries: int,
        frequency: int,
    ):
        retries = 0
        finality = 0

        while finality < required_confirmations and retries <= max_number_of_retries:
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            # Sleep between attempts (except for first try)
            if retries > 0:
                time.sleep(frequency)
            
            retries += 1

            try:
                response = NodeRequest.finality_status(ual)
                finality = response.get("finality", 0)
                if finality >= required_confirmations:
                    break
            except Exception:
                finality = 0

        return finality

def finality(
        ual, 
        required_confirmations, 
        max_number_of_retries, 
        frequency
    ):
        finality_id = 0
        retries = 0

        while finality_id < required_confirmations and retries < max_number_of_retries:
            
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            if retries > 0:
                time.sleep(frequency)
            
            retries += 1

            try:
                response = NodeRequest.finality(ual) 
                operation_id = response.json().get("operationId", 0)
                if operation_id >= required_confirmations:
                    finality_id = operation_id 
                
            except Exception as e:
                finality_id = 0 
                print(f"Retry {retries + 1}/{max_number_of_retries} failed: {e}")
            
            return finality_id
