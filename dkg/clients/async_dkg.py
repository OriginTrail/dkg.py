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


from dkg.modules.asset.async_asset import AsyncKnowledgeAsset
from dkg.modules.graph.async_graph import AsyncGraph
from dkg.managers.async_manager import AsyncRequestManager
from dkg.modules.async_module import AsyncModule
from dkg.modules.node.async_node import AsyncNode
from dkg.types import UAL, Address, ChecksumAddress
from dkg.utils.ual import format_ual, parse_ual
from dkg.services.input_service import InputService
from dkg.providers.blockchain.async_blockchain import AsyncBlockchainProvider
from dkg.providers.node.async_node_http import AsyncNodeHTTPProvider
from dkg.services.node_services.async_node_service import AsyncNodeService
from dkg.modules.paranet.async_paranet import AsyncParanet
from dkg.services.blockchain_services.async_blockchain_service import (
    AsyncBlockchainService,
)


class AsyncDKG(AsyncModule):
    asset: AsyncKnowledgeAsset
    node: AsyncNode
    graph: AsyncGraph
    paranet: AsyncParanet

    def __init__(
        self,
        node_provider: AsyncNodeHTTPProvider,
        blockchain_provider: AsyncBlockchainProvider,
        config: dict = {},
    ):
        self.manager = AsyncRequestManager(node_provider, blockchain_provider)

        self.initialize_services(config)

        modules = {
            "asset": AsyncKnowledgeAsset(
                self.manager,
                self.input_service,
                self.node_service,
                self.blockchain_service,
            ),
            "node": AsyncNode(self.manager, self.node_service),
            "graph": AsyncGraph(self.manager, self.input_service, self.node_service),
            "paranet": AsyncParanet(
                self.manager, self.input_service, self.blockchain_service
            ),
        }
        self._attach_modules(modules)

        self._setup_backwards_compatibility()

    def _setup_backwards_compatibility(self):
        # Create async wrapper methods
        async def graph_get(*args, **kwargs):
            return await self.asset.get(*args, **kwargs)

        async def graph_create(*args, **kwargs):
            return await self.asset.create(*args, **kwargs)

        # Attach methods to graph
        self.graph.get = graph_get
        self.graph.create = graph_create

    def initialize_services(self, config: dict = {}):
        self.input_service = InputService(self.manager, config)
        self.node_service = AsyncNodeService(self.manager)
        self.blockchain_service = AsyncBlockchainService(self.manager)

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

    @property
    def node_provider(self) -> AsyncNodeHTTPProvider:
        return self.manager.node_provider

    @node_provider.setter
    def node_provider(self, node_provider: AsyncNodeHTTPProvider) -> None:
        self.manager.node_provider = node_provider

    @property
    def blockchain_provider(self) -> AsyncBlockchainProvider:
        return self.manager.blockchain_provider

    @blockchain_provider.setter
    def blockchain_provider(self, blockchain_provider: AsyncBlockchainProvider) -> None:
        self.manager.blockchain_provider = blockchain_provider
