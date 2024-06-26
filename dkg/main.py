# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from functools import wraps

from dkg.assertion import Assertion
from dkg.asset import KnowledgeAsset
from dkg.graph import Graph
from dkg.manager import DefaultRequestManager
from dkg.module import Module
from dkg.network import Network
from dkg.node import Node
from dkg.paranet import Paranet
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.types import UAL, Address, ChecksumAddress
from dkg.utils.ual import format_ual, parse_ual


class DKG(Module):
    assertion: Assertion
    asset: KnowledgeAsset
    paranet: Paranet
    network: Network
    node: Node
    graph: Graph

    @staticmethod
    @wraps(format_ual)
    def format_ual(
        blockchain: str, contract_address: Address | ChecksumAddress, token_id: int
    ) -> UAL:
        return format_ual(blockchain, contract_address, token_id)

    @staticmethod
    @wraps(parse_ual)
    def parse_ual(ual: UAL) -> dict[str, str | Address | int]:
        return parse_ual(ual)

    def __init__(
        self,
        node_provider: NodeHTTPProvider,
        blockchain_provider: BlockchainProvider,
    ):
        self.manager = DefaultRequestManager(node_provider, blockchain_provider)
        modules = {
            "assertion": Assertion(self.manager),
            "asset": KnowledgeAsset(self.manager),
            "paranet": Paranet(self.manager),
            "network": Network(self.manager),
            "node": Node(self.manager),
            "graph": Graph(self.manager),
        }
        self._attach_modules(modules)

    @property
    def node_provider(self) -> NodeHTTPProvider:
        return self.manager.node_provider

    @node_provider.setter
    def node_provider(self, node_provider: NodeHTTPProvider) -> None:
        self.manager.node_provider = node_provider

    @property
    def blockchain_provider(self) -> BlockchainProvider:
        return self.manager.blockchain_provider

    @blockchain_provider.setter
    def blockchain_provider(self, blockchain_provider: BlockchainProvider) -> None:
        self.manager.blockchain_provider = blockchain_provider
