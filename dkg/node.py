from dkg.module import Module
from dkg.method import Method
from dkg.manager import DefaultRequestManager
from dkg._utils.node_request import NodeRequest


class Node(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _info = Method(NodeRequest.info)

    @property
    def info(self) -> dict[str, str]:
        return self._info()

    _get_bid_suggestion = Method(NodeRequest.bid_suggestion)
    _local_store = Method(NodeRequest.local_store)
    _publish = Method(NodeRequest.publish)
    _get = Method(NodeRequest.get)
    _query = Method(NodeRequest.query)
