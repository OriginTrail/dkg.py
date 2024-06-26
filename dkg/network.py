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

from dkg.constants import DEFAULT_HASH_FUNCTION_ID
from dkg.dataclasses import BidSuggestionRange
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import DataHexStr
from dkg.utils.blockchain_request import BlockchainRequest
from dkg.utils.node_request import NodeRequest


class Network(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _get_asset_storage_address = Method(BlockchainRequest.get_asset_storage_address)

    _get_bid_suggestion = Method(NodeRequest.bid_suggestion)

    def get_bid_suggestion(
        self,
        public_assertion_id: DataHexStr,
        size_in_bytes: int,
        epochs_number: int,
        range: BidSuggestionRange = BidSuggestionRange.LOW,
    ) -> int:
        content_asset_storage_address = self._get_asset_storage_address(
            "ContentAssetStorage"
        )

        response = self._get_bid_suggestion(
            self.manager.blockchain_provider.blockchain_id,
            epochs_number,
            size_in_bytes,
            content_asset_storage_address,
            public_assertion_id,
            DEFAULT_HASH_FUNCTION_ID,
            range,
        )

        return (
            int(response["bidSuggestion"])
            if range != BidSuggestionRange.ALL
            else response
        )
