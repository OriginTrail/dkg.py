from dkg.providers import NodeHTTPProvider, BlockchainProvider
from dkg.types import NodeEndpoint, BlockchainEndpoint, BlockchainResponse, NodeResponse
from dkg.exceptions import InvalidRequest
from typing import Any
from dataclasses import asdict


class DefaultRequestManager:
    def __init__(self, node_provider: NodeHTTPProvider, blockchain_provider: BlockchainProvider):
        self.node_provider = node_provider
        self.blockchain_provider = blockchain_provider

    def blocking_request(
        self, request: BlockchainEndpoint | NodeEndpoint, params: Any = None
    ) -> BlockchainResponse | NodeResponse:
        match request:
            case BlockchainEndpoint():
                pass
            case NodeEndpoint():
                return self.node_provider.make_request(**asdict(request), data=params)
            case _:
                raise InvalidRequest(
                    "Invalid Request. Manager can only process Blockchain/Node requests."
                )
