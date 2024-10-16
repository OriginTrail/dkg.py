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
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.utils.node_request import NodeRequest
from dkg.utils.blockchain_request import BlockchainRequest
from dkg.types import Address


class Node(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _info = Method(NodeRequest.info)

    @property
    def info(self) -> NodeResponseDict:
        return self._info()

    _get_identity_id = Method(BlockchainRequest.get_identity_id)

    def get_identity_id(self, operational: Address) -> int:
        return self._get_identity_id(operational)
