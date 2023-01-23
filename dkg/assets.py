from dkg.module import Module
from dkg.method import Method
from dkg._utils.node_request import NodeRequest
from dkg._utils.blockchain_request import BlockchainRequest


class ContentAsset:
    _local_store = Method(NodeRequest.local_store)

    _increase_allowance = Method(BlockchainRequest.increase_allowance)
    _decrease_allowance = Method(BlockchainRequest.decrease_allowance)
    _create = Method(BlockchainRequest.create_asset)
    _publish = Method(NodeRequest.publish)

    def create(self):
        pass

    _get = Method(NodeRequest.get)
    _owner = Method(BlockchainRequest.owner_of)

    def get(self):
        pass


class Assets(Module):
    ContentAsset: ContentAsset
