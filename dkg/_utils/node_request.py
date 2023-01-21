from dataclasses import dataclass, field
from dkg.dataclasses import HTTPRequestMethod
from dkg.types import Address, DataHexStr
from typing import Type


@dataclass
class NodeEndpoint:
    method: HTTPRequestMethod
    path: str
    params: dict[str, Type] = field(default_factory=dict)
    data: dict[str, Type] = field(default_factory=dict)


class NodeRequest:
    info = NodeEndpoint(method=HTTPRequestMethod.GET, path='info')
    bid_suggestion = NodeEndpoint(
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
    local_store = NodeEndpoint(method=HTTPRequestMethod.POST, path='local-store')
    publish = NodeEndpoint(method=HTTPRequestMethod.POST, path='publish')
    get = NodeEndpoint(method=HTTPRequestMethod.POST, path='get')
    query = NodeEndpoint(method=HTTPRequestMethod.POST, path='query')
