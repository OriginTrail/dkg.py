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

from dkg.dataclasses import BaseIncentivesPoolParams, ParanetIncentivizationType
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import Address, UAL, HexStr
from dkg.utils.blockchain_request import BlockchainRequest
from dkg.utils.ual import parse_ual


class Paranet(Module):
    @dataclass
    class NeuroWebIncentivesPoolParams(BaseIncentivesPoolParams):
        neuro_emission_multiplier: float
        operator_percentage: float
        voters_percentage: float

        def to_contract_args(self) -> dict:
            return {
                "tracToNeuroEmissionMultiplier": int(
                    self.neuro_emission_multiplier * (10**12)
                ),
                "paranetOperatorRewardPercentage": int(self.operator_percentage * 100),
                "paranetIncentivizationProposalVotersRewardPercentage": int(
                    self.voters_percentage * 100
                ),
            }

    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager
        self.incentives_pools_deployment_functions = {
            ParanetIncentivizationType.NEUROWEB: self._deploy_neuro_incentives_pool,
        }

    _register_paranet = Method(BlockchainRequest.register_paranet)

    def create(
        self, ual: UAL, name: str, description: str
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        receipt: TxReceipt = self._register_paranet(
            knowledge_asset_storage,
            knowledge_asset_token_id,
            name,
            description,
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_asset_storage, knowledge_asset_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _deploy_neuro_incentives_pool = Method(
        BlockchainRequest.deploy_neuro_incentives_pool
    )

    def deploy_incentives_contract(
        self,
        ual: UAL,
        incentives_pool_parameters: NeuroWebIncentivesPoolParams,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> dict[str, str | HexStr | TxReceipt]:
        deploy_incentives_pool_fn = self.incentives_pools_deployment_functions.get(
            incentives_type,
            None,
        )

        if deploy_incentives_pool_fn is None:
            raise ValueError(
                f"{incentives_type} Incentive Type isn't supported. Supported "
                f"Incentive Types: {self.incentives_pools_deployment_functions.keys()}"
            )

        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        receipt: TxReceipt = deploy_incentives_pool_fn(
            knowledge_asset_storage,
            knowledge_asset_token_id,
            **incentives_pool_parameters.to_contract_args(),
        )

        events = self.manager.blockchain_provider.decode_logs_event(
            receipt,
            "ParanetIncentivesPoolFactory",
            "ParanetIncetivesPoolDeployed",
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_asset_storage, knowledge_asset_token_id],
                )
            ),
            "incentivesPoolAddress": events[0].args["incentivesPool"]["addr"],
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _get_incentives_pool_address = Method(BlockchainRequest.get_incentives_pool_address)

    def get_incentives_pool_address(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> Address:
        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )
        paranet_id = Web3.solidity_keccak(
            ["address", "uint256"], [knowledge_asset_storage, knowledge_asset_token_id]
        )

        return self._get_incentives_pool_address(paranet_id, incentives_type)

    _register_paranet_service = Method(BlockchainRequest.register_paranet_service)

    def create_service(
        self, ual: UAL, name: str, description: str, addresses: list[Address]
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        receipt: TxReceipt = self._register_paranet_service(
            knowledge_asset_storage,
            knowledge_asset_token_id,
            name,
            description,
            addresses,
        )

        return {
            "paranetServiceUAL": ual,
            "paranetServiceId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_asset_storage, knowledge_asset_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _add_paranet_services = Method(BlockchainRequest.add_paranet_services)

    def add_services(
        self, ual: UAL, services_uals: list[UAL]
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_paranet_ual = parse_ual(ual)
        paranet_knowledge_asset_storage, paranet_knowledge_asset_token_id = (
            parsed_paranet_ual["contract_address"],
            parsed_paranet_ual["token_id"],
        )

        parsed_service_uals = []
        for service_ual in services_uals:
            parsed_service_ual = parse_ual(service_ual)
            (service_knowledge_asset_storage, service_knowledge_asset_token_id) = (
                parsed_service_ual["contract_address"],
                parsed_service_ual["token_id"],
            )

            parsed_service_uals.append(
                {
                    "knowledgeAssetStorageContract": service_knowledge_asset_storage,
                    "tokenId": service_knowledge_asset_token_id,
                }
            )

        receipt: TxReceipt = self._add_paranet_services(
            paranet_knowledge_asset_storage,
            paranet_knowledge_asset_token_id,
            parsed_service_uals,
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [paranet_knowledge_asset_storage, paranet_knowledge_asset_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _is_knowledge_miner_registered = Method(
        BlockchainRequest.is_knowledge_miner_registered
    )

    def is_knowledge_miner(self, ual: UAL, address: Address | None = None) -> bool:
        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        paranet_id = Web3.solidity_keccak(
            ["address", "uint256"], [knowledge_asset_storage, knowledge_asset_token_id]
        )

        return self._is_knowledge_miner_registered(
            paranet_id, address or self.manager.blockchain_provider.account.address
        )

    _owner_of = Method(BlockchainRequest.owner_of)

    def is_operator(self, ual: UAL, address: Address | None = None) -> bool:
        knowledge_asset_token_id = parse_ual(ual)["token_id"]

        return self._owner_of(knowledge_asset_token_id) == (
            address or self.manager.blockchain_provider.account.address
        )

    _is_proposal_voter = Method(BlockchainRequest.is_proposal_voter)

    def is_voter(
        self,
        ual: UAL,
        address: Address | None = None,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> bool:
        return self._is_proposal_voter(
            contract=self._get_incentives_pool_contract(ual, incentives_type),
            addr=address or self.manager.blockchain_provider.account.address,
        )

    _get_claimable_knowledge_miner_reward_amount = Method(
        BlockchainRequest.get_claimable_knowledge_miner_reward_amount
    )

    def calculate_claimable_miner_reward_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_knowledge_miner_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _get_claimable_all_knowledge_miners_reward_amount = Method(
        BlockchainRequest.get_claimable_all_knowledge_miners_reward_amount
    )

    def calculate_all_claimable_miner_rewards_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_all_knowledge_miners_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _claim_knowledge_miner_reward = Method(
        BlockchainRequest.claim_knowledge_miner_reward
    )

    def claim_miner_reward(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> dict[str, str | HexStr | TxReceipt]:
        receipt: TxReceipt = self._claim_knowledge_miner_reward(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_asset_storage, knowledge_asset_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _get_claimable_paranet_operator_reward_amount = Method(
        BlockchainRequest.get_claimable_paranet_operator_reward_amount
    )

    def calculate_claimable_operator_reward_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_paranet_operator_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _claim_paranet_operator_reward = Method(
        BlockchainRequest.claim_paranet_operator_reward
    )

    def claim_operator_reward(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> dict[str, str | HexStr | TxReceipt]:
        receipt: TxReceipt = self._claim_paranet_operator_reward(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_asset_storage, knowledge_asset_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _get_claimable_proposal_voter_reward_amount = Method(
        BlockchainRequest.get_claimable_proposal_voter_reward_amount
    )

    def calculate_claimable_voter_reward_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_proposal_voter_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _get_claimable_all_proposal_voters_reward_amount = Method(
        BlockchainRequest.get_claimable_all_proposal_voters_reward_amount
    )

    def calculate_all_claimable_voters_reward_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_all_proposal_voters_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _claim_incentivization_proposal_voter_reward = Method(
        BlockchainRequest.claim_incentivization_proposal_voter_reward
    )

    def claim_voter_reward(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> dict[str, str | HexStr | TxReceipt]:
        receipt: TxReceipt = self._claim_incentivization_proposal_voter_reward(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_asset_storage, knowledge_asset_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _get_updating_knowledge_asset_states = Method(
        BlockchainRequest.get_updating_knowledge_asset_states
    )
    _process_updated_knowledge_asset_states_metadata = Method(
        BlockchainRequest.process_updated_knowledge_asset_states_metadata
    )

    def update_claimable_rewards(self, ual: UAL) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        paranet_id = Web3.solidity_keccak(
            ["address", "uint256"], [knowledge_asset_storage, knowledge_asset_token_id]
        )

        updating_states = self._get_updating_knowledge_asset_states(
            self.manager.blockchain_provider.account.address,
            paranet_id,
        )
        receipt: TxReceipt = self._process_updated_knowledge_asset_states_metadata(
            knowledge_asset_storage,
            knowledge_asset_token_id,
            0,
            len(updating_states),
        )

        return {
            "paranetUAL": ual,
            "paranetId": paranet_id,
            "operation": json.loads(Web3.to_json(receipt)),
        }

    def _get_incentives_pool_contract(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> str | dict[str, str]:
        incentives_pool_name = f"Paranet{str(incentives_type)}IncentivesPool"
        is_incentives_pool_cached = (
            incentives_pool_name in self.manager.blockchain_provider.contracts.keys()
        )

        return (
            incentives_pool_name
            if is_incentives_pool_cached
            else {
                "name": incentives_pool_name,
                "address": self.get_incentives_pool_address(ual, incentives_type),
            }
        )
