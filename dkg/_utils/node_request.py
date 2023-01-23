from dataclasses import dataclass, field
from dkg.dataclasses import HTTPRequestMethod
from dkg.types import Address, DataHexStr
from typing import Type


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
    local_store = NodeCall(method=HTTPRequestMethod.POST, path='local-store')
    publish = NodeCall(method=HTTPRequestMethod.POST, path='publish')
    get = NodeCall(method=HTTPRequestMethod.POST, path='get')
    query = NodeCall(method=HTTPRequestMethod.POST, path='query')
