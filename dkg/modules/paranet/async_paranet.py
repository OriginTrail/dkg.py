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

import json

from dataclasses import dataclass
from web3 import Web3
from web3.types import TxReceipt

from dkg.dataclasses import (
    BaseIncentivesPoolParams,
    ParanetIncentivizationType,
)
from dkg.managers.async_manager import AsyncRequestManager
from dkg.modules.async_module import AsyncModule
from dkg.types import Address, UAL, HexStr
from dkg.utils.ual import parse_ual, get_paranet_id, get_paranet_ual_details
from dkg.services.input_service import InputService
from dkg.services.blockchain_services.async_blockchain_service import (
    AsyncBlockchainService,
)
from dkg.exceptions import ValidationError
from dkg.constants import BlockchainIds


class AsyncParanet(AsyncModule):
    @dataclass
    class NeuroWebIncentivesPoolParams(BaseIncentivesPoolParams):
        neuro_emission_multiplier: float
        operator_percentage: float
        voters_percentage: float

        def to_contract_args(self, incentive_type: ParanetIncentivizationType) -> dict:
            return {
                "trac_to_neuro_emission_multiplier": int(
                    self.neuro_emission_multiplier
                    * (
                        10**12
                        if incentive_type == ParanetIncentivizationType.NEUROWEB
                        else 10**18
                    )
                ),
                "paranet_operator_reward_percentage": int(
                    self.operator_percentage * 100
                ),
                "paranet_incentivization_proposal_voters_reward_percentage": int(
                    self.voters_percentage * 100
                ),
            }

    def __init__(
        self,
        manager: AsyncRequestManager,
        input_service: InputService,
        blockchain_service: AsyncBlockchainService,
    ):
        self.manager = manager
        self.input_service = input_service
        self.blockchain_service = blockchain_service
        self.incentive_type = (
            ParanetIncentivizationType.NEUROWEB
            if self.manager.blockchain_provider.blockchain_id
            in (
                BlockchainIds.NEUROWEB_DEVNET,
                BlockchainIds.NEUROWEB_TESTNET,
                BlockchainIds.NEUROWEB_MAINNET,
                BlockchainIds.HARDHAT_1,
                BlockchainIds.HARDHAT_2,
            )
            else ParanetIncentivizationType.NEUROWEB_ERC20
        )

    async def create(
        self,
        ual: UAL,
        options: dict = {},
    ) -> dict[str, str | HexStr | TxReceipt]:
        arguments = self.input_service.get_paranet_create_arguments(options)
        name = arguments["paranet_name"]
        description = arguments["paranet_description"]
        paranet_nodes_access_policy = arguments["paranet_nodes_access_policy"]
        paranet_miners_access_policy = arguments["paranet_miners_access_policy"]

        (
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            paranet_knowledge_asset_token_id,
        ) = get_paranet_ual_details(ual)

        receipt: TxReceipt = await self.blockchain_service.register_paranet(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            paranet_knowledge_asset_token_id,
            name,
            description,
            paranet_nodes_access_policy,
            paranet_miners_access_policy,
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(get_paranet_id(ual)),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    # _add_paranet_curated_nodes = Method(BlockchainRequest.add_paranet_curated_nodes)

    # def add_curated_nodes(
    #     self, paranet_ual: UAL, identity_ids: list[int]
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._add_paranet_curated_nodes(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #         identity_ids,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _remove_paranet_curated_nodes = Method(
    #     BlockchainRequest.remove_paranet_curated_nodes
    # )

    # def remove_curated_nodes(
    #     self, paranet_ual: UAL, identity_ids: list[int]
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._remove_paranet_curated_nodes(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #         identity_ids,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _request_paranet_curated_node_access = Method(
    #     BlockchainRequest.request_paranet_curated_node_access
    # )

    # def request_curated_node_access(
    #     self, paranet_ual: UAL
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._request_paranet_curated_node_access(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _approve_curated_node = Method(BlockchainRequest.approve_curated_node)

    # def approve_curated_node(
    #     self, paranet_ual: UAL, identity_id: int
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._approve_curated_node(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #         identity_id,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _reject_curated_node = Method(BlockchainRequest.reject_curated_node)

    # def reject_curated_node(
    #     self, paranet_ual: UAL, identity_id: int
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._reject_curated_node(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #         identity_id,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _get_curated_nodes = Method(BlockchainRequest.get_curated_nodes)

    # def get_curated_nodes(
    #     self, paranet_ual: UAL
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     paranet_id = get_paranet_id(paranet_ual)

    #     return self._get_curated_nodes(paranet_id)

    # _add_paranet_curated_miners = Method(BlockchainRequest.add_paranet_curated_miners)

    # def add_curated_miners(
    #     self, paranet_ual: UAL, miner_addresses: list[Address]
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._add_paranet_curated_miners(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #         miner_addresses,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _remove_paranet_curated_miners = Method(
    #     BlockchainRequest.remove_paranet_curated_miners
    # )

    # def remove_curated_miners(
    #     self, paranet_ual: UAL, miner_addresses: list[Address]
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._remove_paranet_curated_miners(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #         miner_addresses,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _request_paranet_curated_miner_access = Method(
    #     BlockchainRequest.request_paranet_curated_miner_access
    # )

    # def request_curated_miner_access(
    #     self, paranet_ual: UAL
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._request_paranet_curated_miner_access(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _approve_curated_miner = Method(BlockchainRequest.approve_curated_miner)

    # def approve_curated_miner(
    #     self, paranet_ual: UAL, miner_address: Address
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._approve_curated_miner(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #         miner_address,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _reject_curated_miner = Method(BlockchainRequest.reject_curated_miner)

    # def reject_curated_miner(
    #     self, paranet_ual: UAL, miner_address: Address
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     (
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #     ) = get_paranet_ual_details(paranet_ual)

    #     receipt = self._reject_curated_miner(
    #         paranet_knowledge_collection_storage,
    #         paranet_knowledge_collection_token_id,
    #         paranet_knowledge_asset_token_id,
    #         miner_address,
    #     )

    #     return {
    #         "paranetUAL": paranet_ual,
    #         "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _get_knowledge_miners = Method(BlockchainRequest.get_knowledge_miners)

    def get_knowledge_miners(
        self, paranet_ual: UAL
    ) -> dict[str, str | HexStr | TxReceipt]:
        paranet_id = get_paranet_id(paranet_ual)

        return self._get_knowledge_miners(paranet_id)

    async def deploy_incentives_contract(
        self,
        paranet_ual: UAL,
        incentives_pool_parameters: NeuroWebIncentivesPoolParams,
    ) -> dict[str, str | HexStr | TxReceipt]:
        incentive_types = [item.value for item in ParanetIncentivizationType]
        if self.incentive_type in incentive_types:
            (
                paranet_knowledge_collection_storage,
                paranet_knowledge_collection_token_id,
                paranet_knowledge_asset_token_id,
            ) = get_paranet_ual_details(paranet_ual)

            is_native_reward = (
                True
                if self.incentive_type == ParanetIncentivizationType.NEUROWEB
                else False
            )

            receipt: TxReceipt = await self.blockchain_service.deploy_neuro_incentives_pool(
                is_native_reward=is_native_reward,
                paranet_knowledge_collection_storage=paranet_knowledge_collection_storage,
                paranet_knowledge_collection_token_id=paranet_knowledge_collection_token_id,
                paranet_knowledge_asset_token_id=paranet_knowledge_asset_token_id,
                **incentives_pool_parameters.to_contract_args(self.incentive_type),
            )

            events = self.manager.blockchain_provider.decode_logs_event(
                receipt,
                "ParanetIncentivesPoolFactory",
                "ParanetIncetivesPoolDeployed",
            )

            return {
                "paranetUAL": paranet_ual,
                "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
                "incentivesPoolContractAddress": events[0].args["incentivesPool"][
                    "addr"
                ],
                "operation": json.loads(Web3.to_json(receipt)),
            }

        raise ValueError(
            f"{self.incentive_type} Incentive Type isn't supported. Supported "
            f"Incentive Types: {incentive_types}"
        )

    async def get_incentives_pool_address(
        self,
        paranet_ual: UAL,
    ) -> Address:
        paranet_id = get_paranet_id(paranet_ual)

        return await self.blockchain_service.get_incentives_pool_address(
            paranet_id, self.incentive_type
        )

    async def create_service(
        self, ual: UAL, options: dict = {}
    ) -> dict[str, str | HexStr | TxReceipt]:
        arguments = self.input_service.get_paranet_create_service_arguments(options)
        paranet_service_name = arguments["paranet_service_name"]
        paranet_service_description = arguments["paranet_service_description"]
        paranet_service_addresses = arguments["paranet_service_addresses"]

        parsed_ual = parse_ual(ual)
        knowledge_collection_storage, knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )
        knowledge_asset_token_id = parsed_ual.get("knowledge_asset_token_id", None)

        if not knowledge_asset_token_id:
            raise ValidationError(
                "Invalid paranet service UAL! Knowledge asset token id is required!"
            )

        receipt: TxReceipt = await self.blockchain_service.register_paranet_service(
            knowledge_collection_storage,
            knowledge_collection_token_id,
            knowledge_asset_token_id,
            paranet_service_name,
            paranet_service_description,
            paranet_service_addresses,
        )

        return {
            "paranetServiceUAL": ual,
            "paranetServiceId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256", "uint256"],
                    [
                        knowledge_collection_storage,
                        knowledge_collection_token_id,
                        knowledge_asset_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    async def add_services(
        self, paranet_ual: UAL, services_uals: list[UAL]
    ) -> dict[str, str | HexStr | TxReceipt]:
        (
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            paranet_knowledge_asset_token_id,
        ) = get_paranet_ual_details(paranet_ual)

        parsed_service_uals = []
        for service_ual in services_uals:
            parsed_service_ual = parse_ual(service_ual)
            (
                service_knowledge_collection_storage,
                service_knowledge_collection_token_id,
                service_knowledge_asset_token_id,
            ) = (
                parsed_service_ual["contract_address"],
                parsed_service_ual["knowledge_collection_token_id"],
                parsed_service_ual.get("knowledge_asset_token_id", None),
            )

            if not service_knowledge_asset_token_id:
                raise ValidationError(
                    "Invalid paranet service UAL! Knowledge asset token id is required!"
                )

            parsed_service_uals.append(
                [
                    service_knowledge_collection_storage,
                    service_knowledge_collection_token_id,
                    service_knowledge_asset_token_id,
                ]
            )

        receipt: TxReceipt = await self.blockchain_service.add_paranet_services(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            paranet_knowledge_asset_token_id,
            parsed_service_uals,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(get_paranet_id(paranet_ual)),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    async def is_knowledge_miner(
        self,
        paranet_ual: UAL,
        address: Address | None = None,
    ) -> bool:
        paranet_id = get_paranet_id(paranet_ual)

        return await self.blockchain_service.is_knowledge_miner_registered(
            paranet_id, address or self.manager.blockchain_provider.account.address
        )

    async def is_operator(
        self,
        paranet_ual: UAL,
        address: Address | None = None,
    ) -> bool:
        incentives_pool_address = await self.get_incentives_pool_address(paranet_ual)

        self.blockchain_service.set_incentives_pool(incentives_pool_address)

        return await self.blockchain_service.is_paranet_operator(
            operator_address=address or self.manager.blockchain_provider.account.address
        )

    async def is_voter(
        self,
        paranet_ual: UAL,
        address: Address | None = None,
    ) -> bool:
        incentives_pool_address = await self.get_incentives_pool_address(paranet_ual)

        self.blockchain_service.set_incentives_pool(incentives_pool_address)

        return await self.blockchain_service.is_proposal_voter(
            address=address or self.manager.blockchain_provider.account.address,
        )

    # _get_claimable_knowledge_miner_reward_amount = Method(
    #     BlockchainRequest.get_claimable_knowledge_miner_reward_amount
    # )

    # def calculate_claimable_miner_reward_amount(
    #     self,
    #     ual: UAL,
    #
    # ) -> int:
    #     return self._get_claimable_knowledge_miner_reward_amount(
    #         contract=self._get_incentives_pool_contract(ual)
    #     )

    # _get_claimable_all_knowledge_miners_reward_amount = Method(
    #     BlockchainRequest.get_claimable_all_knowledge_miners_reward_amount
    # )

    # def calculate_all_claimable_miner_rewards_amount(
    #     self,
    #     ual: UAL,
    #
    # ) -> int:
    #     return self._get_claimable_all_knowledge_miners_reward_amount(
    #         contract=self._get_incentives_pool_contract(ual)
    #     )

    # _claim_knowledge_miner_reward = Method(
    #     BlockchainRequest.claim_knowledge_miner_reward
    # )

    # def claim_miner_reward(
    #     self,
    #     ual: UAL,
    #
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     receipt: TxReceipt = self._claim_knowledge_miner_reward(
    #         contract=self._get_incentives_pool_contract(ual)
    #     )

    #     paranet_id = get_paranet_id(ual)

    #     return {
    #         "paranetUAL": ual,
    #         "paranetId": Web3.to_hex(paranet_id),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _get_claimable_paranet_operator_reward_amount = Method(
    #     BlockchainRequest.get_claimable_paranet_operator_reward_amount
    # )

    # def calculate_claimable_operator_reward_amount(
    #     self,
    #     ual: UAL,
    #
    # ) -> int:
    #     return self._get_claimable_paranet_operator_reward_amount(
    #         contract=self._get_incentives_pool_contract(ual)
    #     )

    # _claim_paranet_operator_reward = Method(
    #     BlockchainRequest.claim_paranet_operator_reward
    # )

    # def claim_operator_reward(
    #     self,
    #     ual: UAL,
    #
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     receipt: TxReceipt = self._claim_paranet_operator_reward(
    #         contract=self._get_incentives_pool_contract(ual)
    #     )

    #     paranet_id = get_paranet_id(ual)

    #     return {
    #         "paranetUAL": ual,
    #         "paranetId": Web3.to_hex(paranet_id),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # _get_claimable_proposal_voter_reward_amount = Method(
    #     BlockchainRequest.get_claimable_proposal_voter_reward_amount
    # )

    # def calculate_claimable_voter_reward_amount(
    #     self,
    #     ual: UAL,
    #
    # ) -> int:
    #     return self._get_claimable_proposal_voter_reward_amount(
    #         contract=self._get_incentives_pool_contract(ual)
    #     )

    # _get_claimable_all_proposal_voters_reward_amount = Method(
    #     BlockchainRequest.get_claimable_all_proposal_voters_reward_amount
    # )

    # def calculate_all_claimable_voters_reward_amount(
    #     self,
    #     ual: UAL,
    #
    # ) -> int:
    #     return self._get_claimable_all_proposal_voters_reward_amount(
    #         contract=self._get_incentives_pool_contract(ual)
    #     )

    # _claim_incentivization_proposal_voter_reward = Method(
    #     BlockchainRequest.claim_incentivization_proposal_voter_reward
    # )

    # def claim_voter_reward(
    #     self,
    #     ual: UAL,
    #
    # ) -> dict[str, str | HexStr | TxReceipt]:
    #     receipt: TxReceipt = self._claim_incentivization_proposal_voter_reward(
    #         contract=self._get_incentives_pool_contract(ual)
    #     )

    #     paranet_id = get_paranet_id(ual)

    #     return {
    #         "paranetUAL": ual,
    #         "paranetId": Web3.to_hex(paranet_id),
    #         "operation": json.loads(Web3.to_json(receipt)),
    #     }

    # def _get_incentives_pool_contract(
    #     self,
    #     ual: UAL,
    # ) -> str | dict[str, str]:
    #     incentives_pool_name = f"Paranet{str(self.incentive_type)}IncentivesPool"
    #     is_incentives_pool_cached = (
    #         incentives_pool_name in self.manager.blockchain_provider.contracts.keys()
    #     )

    #     return (
    #         incentives_pool_name
    #         if is_incentives_pool_cached
    #         else {
    #             "name": incentives_pool_name,
    #             "address": self.get_incentives_pool_address(ual),
    #         }
    #     )
