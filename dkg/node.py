from dkg.dataclasses import NodeResponseDict
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import Address, DataHexStr
from dkg.utils.node_request import NodeRequest


class Node(Module):
    """
    A class to represent a Node in the Decentralized Knowledge Graph (DKG) system.
    This class inherits from the Module class and provides methods for interacting with
    the node.

    Attributes:
        manager (DefaultRequestManager): An instance of DefaultRequestManager for managing
        requests to the node.
    """

    def __init__(self, manager: DefaultRequestManager):
        """
        Initializes a Node object with the given request manager.

        Args:
            manager (DefaultRequestManager): An instance of DefaultRequestManager for managing
            requests to the node.
        """
        self.manager = manager

    _info = Method(NodeRequest.info)

    @property
    def info(self) -> NodeResponseDict:
        """
        Retrieves information about the node.

        Returns:
            NodeResponseDict: A dictionary containing information about the node.
        """
        return self._info()

    _get_bid_suggestion = Method(NodeRequest.bid_suggestion)

    def get_bid_suggestion(
        self,
        blockchain: str,
        epochs_num: int,
        assertion_size: int,
        content_asset_storage_address: Address,
        first_assertion_id: DataHexStr,
        hash_function_id: int,
    ) -> NodeResponseDict:
        """
        Retrieves a bid suggestion for the given parameters.

        Args:
            blockchain (str): The blockchain identifier.
            epochs_num (int): The number of epochs.
            assertion_size (int): The size of the assertion.
            content_asset_storage_address (Address): The address of the content asset storage.
            first_assertion_id (DataHexStr): The identifier of the first assertion.
            hash_function_id (int): The identifier of the hash function used.

        Returns:
            NodeResponseDict: A dictionary containing the bid suggestion.
        """
        return self._get_bid_suggestion(
            blockchain,
            epochs_num,
            assertion_size,
            content_asset_storage_address,
            first_assertion_id,
            hash_function_id,
        )
