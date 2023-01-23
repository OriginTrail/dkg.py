from dkg.module import Module
from dkg.method import Method
from dkg.manager import DefaultRequestManager
from dkg._utils.node_request import NodeRequest
from dkg.dataclasses import NodeResponseDict
from dkg.types import Address, DataHexStr


class Node(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _info = Method(NodeRequest.info)

    @property
    def info(self) -> NodeResponseDict:
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
        return self._get_bid_suggestion(
            blockchain,
            epochs_num,
            assertion_size,
            content_asset_storage_address,
            first_assertion_id,
            hash_function_id,
        )

    _query = Method(NodeRequest.query)
