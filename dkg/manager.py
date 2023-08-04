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

from typing import Any, Type

from dkg.dataclasses import BlockchainResponseDict, NodeResponseDict
from dkg.exceptions import InvalidRequest
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.utils.blockchain_request import ContractInteraction, JSONRPCRequest
from dkg.utils.node_request import NodeCall


class DefaultRequestManager:
    def __init__(
        self, node_provider: NodeHTTPProvider, blockchain_provider: BlockchainProvider
    ):
        self._node_provider = node_provider
        self._blockchain_provider = blockchain_provider

    @property
    def node_provider(self) -> NodeHTTPProvider:
        return self._node_provider

    @node_provider.setter
    def node_provider(self, node_provider: NodeHTTPProvider) -> None:
        self._node_provider = node_provider

    @property
    def blockchain_provider(self) -> BlockchainProvider:
        return self._blockchain_provider

    @blockchain_provider.setter
    def blockchain_provider(self, blockchain_provider: BlockchainProvider) -> None:
        self._blockchain_provider = blockchain_provider

    def blocking_request(
        self,
        request_type: Type[JSONRPCRequest | ContractInteraction | NodeCall],
        request_params: dict[str, Any],
    ) -> BlockchainResponseDict | NodeResponseDict:
        if issubclass(request_type, JSONRPCRequest):
            return self.blockchain_provider.make_json_rpc_request(**request_params)
        elif issubclass(request_type, ContractInteraction):
            return self.blockchain_provider.call_function(**request_params)
        elif issubclass(request_type, NodeCall):
            return self.node_provider.make_request(**request_params)
        else:
            raise InvalidRequest(
                "Invalid Request. Manager can only process Blockchain/Node requests."
            )
