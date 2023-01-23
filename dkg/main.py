from dkg.module import Module
from dkg.node import Node
from dkg.graph import Graph
from dkg.assets import Assets, ContentAsset
from dkg.manager import DefaultRequestManager
from dkg.providers import BaseProvider, BlockchainProvider, NodeHTTPProvider


class DKG(Module):
    def __init__(
        self,
        node_provider: NodeHTTPProvider,
        blockchain_provider: BlockchainProvider,
    ):
        self.manager = DefaultRequestManager(node_provider, blockchain_provider)
        modules = {
            "assets": (
                Assets(),
                {
                    "content": ContentAsset(),
                }
            ),
            "node": Node(self.manager),
            "graph": Graph(),
        }
        self._attach_modules(modules)

    @property
    def provider(self) -> BaseProvider:
        return self.manager.provider

    @provider.setter
    def provider(self, provider: BaseProvider) -> None:
        self.manager.provider = provider
