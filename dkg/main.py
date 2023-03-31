from functools import wraps

from dkg.assets import Assets, ContentAsset
from dkg.graph import Graph
from dkg.manager import DefaultRequestManager
from dkg.module import Module
from dkg.node import Node
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.types import UAL, Address, ChecksumAddress
from dkg.utils.merkle import MerkleTree
from dkg.utils.ual import format_ual, parse_ual


class DKG(Module):
    """
    A class to represent the Decentralized Knowledge Graph (DKG) system.
    This class inherits from the Module class and provides methods for interacting with
    various DKG components.

    Attributes:
        manager (DefaultRequestManager): An instance of DefaultRequestManager for managing
        requests.
        MerkleTree (MerkleTree): A class reference to the MerkleTree utility class.
    """

    MerkleTree = MerkleTree

    @staticmethod
    @wraps(format_ual)
    def format_ual(
        blockchain: str, contract_address: Address | ChecksumAddress, token_id: int
    ) -> UAL:
        """
        Formats the given parameters into a Universal Asset Locator (UAL).

        Args:
            blockchain (str): The blockchain identifier.
            contract_address (Address | ChecksumAddress): The contract address associated
            with the asset.
            token_id (int): The token ID of the asset.

        Returns:
            UAL: A Universal Asset Locator string.
        """
        return format_ual(blockchain, contract_address, token_id)

    @staticmethod
    @wraps(parse_ual)
    def parse_ual(ual: UAL) -> dict[str, str | Address | int]:
        """
        Parses a Universal Asset Locator (UAL) string into its components.

        Args:
            ual (UAL): The Universal Asset Locator string to parse.

        Returns:
            dict[str, str | Address | int]: A dictionary containing the parsed components
            of the UAL.
        """
        return parse_ual(ual)

    def __init__(
        self,
        node_provider: NodeHTTPProvider,
        blockchain_provider: BlockchainProvider,
    ):
        """
        Initializes a DKG object with the given node and blockchain providers.

        Args:
            node_provider (NodeHTTPProvider): An instance of NodeHTTPProvider for interacting
            with the DKG node.
            blockchain_provider (BlockchainProvider): An instance of BlockchainProvider for
            interacting with the blockchain.
        """
        self.manager = DefaultRequestManager(node_provider, blockchain_provider)
        modules = {
            "assets": (
                Assets(),
                {
                    "content": ContentAsset(self.manager),
                },
            ),
            "node": Node(self.manager),
            "graph": Graph(self.manager),
        }
        self._attach_modules(modules)

    @property
    def node_provider(self) -> NodeHTTPProvider:
        """
        Retrieves the node provider.

        Returns:
            NodeHTTPProvider: The current node provider instance.
        """
        return self.manager.node_provider

    @node_provider.setter
    def node_provider(self, node_provider: NodeHTTPProvider) -> None:
        """
        Sets a new node provider.

        Args:
            node_provider (NodeHTTPProvider): An instance of NodeHTTPProvider to be set
            as the new node provider.
        """
        self.manager.node_provider = node_provider

    @property
    def blockchain_provider(self) -> BlockchainProvider:
        """
        Retrieves the blockchain provider.

        Returns:
            BlockchainProvider: The current blockchain provider instance.
        """
        return self.manager.blockchain_provider

    @blockchain_provider.setter
    def blockchain_provider(self, blockchain_provider: BlockchainProvider) -> None:
        """
        Sets a new blockchain provider.

        Args:
            blockchain_provider (BlockchainProvider): An instance of BlockchainProvider
            to be set as the new blockchain provider.
        """
        self.manager.blockchain_provider = blockchain_provider
