from typing import Any, Type

from dkg.dataclasses import BlockchainResponseDict, NodeResponseDict
from dkg.exceptions import InvalidRequest
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.utils.blockchain_request import ContractInteraction
from dkg.utils.node_request import NodeCall


class DefaultRequestManager:
    """
    A class to represent the DefaultRequestManager in the Decentralized Knowledge Graph (DKG)
    system. This class handles requests to the NodeHTTPProvider and BlockchainProvider.

    Attributes:
        _node_provider (NodeHTTPProvider): An instance of NodeHTTPProvider for making requests
        to the DKG node.
        _blockchain_provider (BlockchainProvider): An instance of BlockchainProvider for making
        requests to the blockchain.
    """

    def __init__(
        self, node_provider: NodeHTTPProvider, blockchain_provider: BlockchainProvider
    ):
        """
        Initializes a DefaultRequestManager object with the given NodeHTTPProvider and
        BlockchainProvider instances.

        Args:
            node_provider (NodeHTTPProvider): An instance of NodeHTTPProvider for making
            requests to the DKG node.
            blockchain_provider (BlockchainProvider): An instance of BlockchainProvider
            for making requests to the blockchain.
        """
        self._node_provider = node_provider
        self._blockchain_provider = blockchain_provider

    @property
    def node_provider(self) -> NodeHTTPProvider:
        """
        Getter for the NodeHTTPProvider instance.

        Returns:
            NodeHTTPProvider: The NodeHTTPProvider instance.
        """
        return self._node_provider

    @node_provider.setter
    def node_provider(self, node_provider: NodeHTTPProvider) -> None:
        """
        Setter for the NodeHTTPProvider instance.

        Args:
            node_provider (NodeHTTPProvider): The new NodeHTTPProvider instance.
        """
        self._node_provider = node_provider

    @property
    def blockchain_provider(self) -> BlockchainProvider:
        """
        Getter for the BlockchainProvider instance.

        Returns:
            BlockchainProvider: The BlockchainProvider instance.
        """
        return self._blockchain_provider

    @blockchain_provider.setter
    def blockchain_provider(self, blockchain_provider: BlockchainProvider) -> None:
        """
        Setter for the BlockchainProvider instance.

        Args:
            blockchain_provider (BlockchainProvider): The new BlockchainProvider instance.
        """
        self._blockchain_provider = blockchain_provider

    def blocking_request(
        self,
        request_type: Type[ContractInteraction | NodeCall],
        request_params: dict[str, Any],
    ) -> BlockchainResponseDict | NodeResponseDict:
        """
        Makes a blocking request to either the NodeHTTPProvider or the BlockchainProvider,
        based on the given request type and parameters.

        Args:
            request_type (Type[ContractInteraction | NodeCall]): The type of request to make,
            either a contract interaction or a node call.
            request_params (dict[str, Any]): A dictionary of request parameters.

        Returns:
            BlockchainResponseDict | NodeResponseDict: A dictionary containing the response
            data from the request.

        Raises:
            InvalidRequest: If the request type is not a ContractInteraction or NodeCall.
        """
        if issubclass(request_type, ContractInteraction):
            return self.blockchain_provider.call_function(**request_params)
        elif issubclass(request_type, NodeCall):
            return self.node_provider.make_request(**request_params)
        else:
            raise InvalidRequest(
                "Invalid Request. Manager can only process Blockchain/Node requests."
            )
