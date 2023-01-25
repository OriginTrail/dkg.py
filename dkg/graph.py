from dkg.module import Module
from dkg.method import Method
from dkg._utils.node_request import NodeRequest


class Graph(Module):
    _query = Method(NodeRequest.query)

    def query(self):
        pass
