from dkg.providers import NodeHTTPProvider, BlockchainProvider
from dkg._utils.blockchain_request import ContractInteraction
from dkg._utils.node_request import NodeCall
from dkg.dataclasses import BlockchainResponseDict, NodeResponseDict
from dkg.exceptions import InvalidRequest
from dataclasses import asdict


class DefaultRequestManager:
    def __init__(self, node_provider: NodeHTTPProvider, blockchain_provider: BlockchainProvider):
        self.node_provider = node_provider
        self.blockchain_provider = blockchain_provider

    def blocking_request(
        self, request_params: ContractInteraction | NodeCall
    ) -> BlockchainResponseDict | NodeResponseDict:
        match request_params:
            case ContractInteraction():
                return self.blockchain_provider.call_function(**asdict(request_params))
            case NodeCall():
                return self.node_provider.make_request(**asdict(request_params))
            case _:
                raise InvalidRequest(
                    "Invalid Request. Manager can only process Blockchain/Node requests."
                )
