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

from dkg.dataclasses import NodeResponseDict
from dkg.managers.async_manager import AsyncRequestManager
from dkg.method import Method
from dkg.modules.async_module import AsyncModule
from dkg.request_managers.blockchain_request import BlockchainRequest
from dkg.types import Address
from dkg.services.node_services.async_node_service import AsyncNodeService


class AsyncNode(AsyncModule):
    def __init__(self, manager: AsyncRequestManager, node_service: AsyncNodeService):
        self.manager = manager
        self.node_service = node_service

    @property
    async def info(self) -> NodeResponseDict:
        return await self.node_service.info()

    _get_identity_id = Method(BlockchainRequest.get_identity_id)

    async def get_identity_id(self, operational: Address) -> int:
        return await self._get_identity_id(operational)
