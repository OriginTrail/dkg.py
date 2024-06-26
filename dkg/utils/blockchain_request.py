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

from dataclasses import dataclass, field
from typing import Type

from dkg.dataclasses import ParanetIncentivizationType
from dkg.types import Address, HexStr, Wei


@dataclass
class JSONRPCRequest:
    endpoint: str
    args: dict[str, Type] = field(default_factory=dict)


@dataclass
class ContractInteraction:
    contract: str | None = None
    function: str = field(default_factory=str)
    args: dict[str, Type] = field(default_factory=dict)

    def __post_init__(self):
        if not self.function:
            raise ValueError(
                "'function' is a required field and cannot be None or empty"
            )


@dataclass
class ContractTransaction(ContractInteraction):
    gas_price: Wei | None = None
    gas_limit: Wei | None = None


@dataclass
class ContractCall(ContractInteraction):
    pass


class BlockchainRequest:
    chain_id = JSONRPCRequest("chain_id")
    get_block = JSONRPCRequest("get_block", args={"block_identifier": str | int})

    get_contract_address = ContractCall(
        contract="Hub",
        function="getContractAddress",
        args={"contractName": str},
    )
    get_asset_storage_address = ContractCall(
        contract="Hub",
        function="getAssetStorageAddress",
        args={"assetStorageName": str},
    )

    allowance = ContractCall(
        contract="Token",
        function="allowance",
        args={"owner": Address, "spender": Address}
    )
    increase_allowance = ContractTransaction(
        contract="Token",
        function="increaseAllowance",
        args={"spender": Address, "addedValue": Wei},
    )
    decrease_allowance = ContractTransaction(
        contract="Token",
        function="decreaseAllowance",
        args={"spender": Address, "subtractedValue": Wei},
    )

    create_asset = ContractTransaction(
        contract="ContentAsset",
        function="createAsset",
        args={"args": dict[str, bytes | int | Wei | bool]},
    )
    burn_asset = ContractTransaction(
        contract="ContentAsset",
        function="burnAsset",
        args={"tokenId": int},
    )
    update_asset_state = ContractTransaction(
        contract="ContentAsset",
        function="updateAssetState",
        args={
            "tokenId": int,
            "assertionId": bytes | HexStr,
            "size": int,
            "triplesNumber": int,
            "chunksNumber": int,
            "updateTokenAmount": int,
        },
    )
    cancel_asset_state_update = ContractTransaction(
        contract="ContentAsset",
        function="cancelAssetStateUpdate",
        args={"tokenId": int},
    )
    extend_asset_storing_period = ContractTransaction(
        contract="ContentAsset",
        function="extendAssetStoringPeriod",
        args={"tokenId": int, "epochsNumber": int, "tokenAmount": int},
    )
    increase_asset_token_amount = ContractTransaction(
        contract="ContentAsset",
        function="increaseAssetTokenAmount",
        args={"tokenId": int, "tokenAmount": int},
    )
    increase_asset_update_token_amount = ContractTransaction(
        contract="ContentAsset",
        function="increaseAssetUpdateTokenAmount",
        args={"tokenId": int, "tokenAmount": int},
    )

    transfer_asset = ContractTransaction(
        contract="ContentAssetStorage",
        function="transferFrom",
        args={"from": Address, "to": Address, "tokenId": int},
    )
    get_assertion_ids = ContractCall(
        contract="ContentAssetStorage",
        function="getAssertionIds",
        args={"tokenId": int},
    )
    get_assertion_id_by_index = ContractCall(
        contract="ContentAssetStorage",
        function="getAssertionIdByIndex",
        args={"tokenId": int, "index": int},
    )
    get_latest_assertion_id = ContractCall(
        contract="ContentAssetStorage",
        function="getLatestAssertionId",
        args={"tokenId": int},
    )
    owner_of = ContractCall(
        contract="ContentAssetStorage",
        function="ownerOf",
        args={"tokenId": int},
    )

    get_unfinalized_state = ContractCall(
        contract="UnfinalizedStateStorage",
        function="getUnfinalizedState",
        args={"tokenId": int},
    )

    get_service_agreement_data = ContractCall(
        contract="ServiceAgreementStorageProxy",
        function="getAgreementData",
        args={"agreementId": bytes | HexStr},
    )

    get_assertion_size = ContractCall(
        contract="AssertionStorage",
        function="getAssertionSize",
        args={"assertionId": bytes | HexStr},
    )

    # Paranets
    register_paranet = ContractTransaction(
        contract="Paranet",
        function="registerParanet",
        args={
            "paranetKAStorageContract": Address,
            "paranetKATokenId": int,
            "paranetName": str,
            "paranetDescription": str,
        },
    )
    add_paranet_services = ContractTransaction(
        contract="Paranet",
        function="addParanetServices",
        args={
            "paranetKAStorageContract": Address,
            "paranetKATokenId": int,
            "services": dict[str, Address | int],
        },
    )
    register_paranet_service = ContractTransaction(
        contract="Paranet",
        function="registerParanetService",
        args={
            "paranetServiceKAStorageContract": Address,
            "paranetServiceKATokenId": int,
            "paranetServiceName": str,
            "paranetServiceDescription": str,
            "paranetServiceAddresses": list[Address],
        },
    )
    mint_knowledge_asset = ContractTransaction(
        contract="Paranet",
        function="mintKnowledgeAsset",
        args={
            "paranetKAStorageContract": Address,
            "paranetKATokenId": int,
            "knowledgeAssetArgs": dict[str, bytes | int | Wei | bool],
        },
    )
    submit_knowledge_asset = ContractTransaction(
        contract="Paranet",
        function="submitKnowledgeAsset",
        args={
            "paranetKAStorageContract": Address,
            "paranetKATokenId": int,
            "knowledgeAssetStorageContract": Address,
            "knowledgeAssetTokenId": int,
        },
    )

    deploy_neuro_incentives_pool = ContractTransaction(
        contract="ParanetIncentivesPoolFactory",
        function="deployNeuroIncentivesPool",
        args={
            "paranetKAStorageContract": Address,
            "paranetKATokenId": int,
            "tracToNeuroEmissionMultiplier": float,
            "paranetOperatorRewardPercentage": float,
            "paranetIncentivizationProposalVotersRewardPercentage": float,
        },
    )
    get_incentives_pool_address = ContractCall(
        contract="ParanetsRegistry",
        function="getIncentivesPoolAddress",
        args={
            "paranetId": HexStr,
            "incentivesPoolType": ParanetIncentivizationType,
        },
    )

    get_updating_knowledge_asset_states = ContractCall(
        contract="ParanetKnowledgeMinersRegistry",
        function="getUpdatingKnowledgeAssetStates",
        args={
            "miner": Address,
            "paranetId": HexStr,
        },
    )
    process_updated_knowledge_asset_states_metadata = ContractTransaction(
        contract="Paranet",
        function="processUpdatedKnowledgeAssetStatesMetadata",
        args={
            "paranetKAStorageContract": Address,
            "paranetKATokenId": int,
            "start": int,
            "end": int,
        },
    )

    is_knowledge_miner_registered = ContractCall(
        contract="ParanetsRegistry",
        function="isKnowledgeMinerRegistered",
        args={
            "paranetId": HexStr,
            "knowledgeMinerAddress": Address,
        },
    )
    is_proposal_voter = ContractCall(
        function="isProposalVoter",
        args={"addr": Address},
    )

    get_claimable_knowledge_miner_reward_amount = ContractCall(
        function="getClaimableKnowledgeMinerRewardAmount",
        args={},
    )
    get_claimable_all_knowledge_miners_reward_amount = ContractCall(
        function="getClaimableAllKnowledgeMinersRewardAmount",
        args={},
    )
    claim_knowledge_miner_reward = ContractTransaction(
        function="claimKnowledgeMinerReward",
        args={},
    )

    get_claimable_paranet_operator_reward_amount = ContractCall(
        function="getClaimableParanetOperatorRewardAmount",
        args={},
    )
    claim_paranet_operator_reward = ContractTransaction(
        function="claimParanetOperatorReward",
        args={},
    )

    get_claimable_proposal_voter_reward_amount = ContractCall(
        function="getClaimableProposalVoterRewardAmount",
        args={},
    )
    get_claimable_all_proposal_voters_reward_amount = ContractCall(
        function="getClaimableAllProposalVotersRewardAmount",
        args={},
    )
    claim_incentivization_proposal_voter_reward = ContractTransaction(
        function="claimIncentivizationProposalVoterReward",
        args={},
    )
