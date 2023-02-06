from dkg.providers import NodeHTTPProvider, BlockchainProvider
from dkg.utils.blockchain_request import ContractInteraction
from dkg.utils.node_request import NodeCall
from dkg.dataclasses import BlockchainResponseDict, NodeResponseDict
from dkg.exceptions import InvalidRequest
from typing import Any, Type


class DefaultRequestManager:
    def __init__(self, node_provider: NodeHTTPProvider, blockchain_provider: BlockchainProvider):
        self.node_provider = node_provider
        self.blockchain_provider = blockchain_provider

    def blocking_request(
        self, request_type: Type[ContractInteraction | NodeCall], request_params: dict[str, Any]
    ) -> BlockchainResponseDict | NodeResponseDict:
        if issubclass(request_type, ContractInteraction):
            return self.blockchain_provider.call_function(**request_params)
        elif issubclass(request_type, NodeCall):
            return self.node_provider.make_request(**request_params)
        else:
            raise InvalidRequest(
                "Invalid Request. Manager can only process Blockchain/Node requests."
            )
