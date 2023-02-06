from dataclasses import dataclass, field
from dkg.dataclasses import HTTPRequestMethod
from dkg.types import Address, DataHexStr, UAL
from typing import Type
from enum import Enum


@dataclass
class NodeCall:
    method: HTTPRequestMethod
    path: str
    params: dict[str, Type] = field(default_factory=dict)
    data: dict[str, Type] = field(default_factory=dict)


class NodeRequest:
    info = NodeCall(method=HTTPRequestMethod.GET, path='info')
    bid_suggestion = NodeCall(
        method=HTTPRequestMethod.GET,
        path='bid-suggestion',
        params={
            'blockchain': str,
            'epochsNumber': int,
            'assertionSize': int,
            'contentAssetStorageAddress': Address,
            'firstAssertionId': DataHexStr,
            'hashFunctionId': int,
        }
    )
    get_operation_result = NodeCall(
        method=HTTPRequestMethod.GET,
        path='{operation}/{operation_id}',
    )

    local_store = NodeCall(method=HTTPRequestMethod.POST, path='local-store')
    publish = NodeCall(method=HTTPRequestMethod.POST, path='publish')
    get = NodeCall(
        method=HTTPRequestMethod.POST,
        path='get',
        data={'id': UAL, 'hashFunctionId': int},
    )
    query = NodeCall(method=HTTPRequestMethod.POST, path='query')


class GetOperationStatus(Enum):
    ASSERTION_EXISTS_LOCAL_START = 'ASSERTION_EXISTS_LOCAL_START'
    ASSERTION_EXISTS_LOCAL_END = 'ASSERTION_EXISTS_LOCAL_END'
    GET_START = 'GET_START'
    GET_INIT_START = 'GET_INIT_START'
    GET_INIT_END = 'GET_INIT_END'
    GET_LOCAL_START = 'GET_LOCAL_START'
    GET_LOCAL_END = 'GET_LOCAL_END'
    GET_REMOTE_START = 'GET_REMOTE_START'
    GET_REMOTE_END = 'GET_REMOTE_END'
    GET_FETCH_FROM_NODES_START = 'GET_FETCH_FROM_NODES_START'
    GET_FETCH_FROM_NODES_END = 'GET_FETCH_FROM_NODES_END'
    GET_END = 'GET_END'
    FAILED = 'FAILED'
    COMPLETED = 'COMPLETED'
