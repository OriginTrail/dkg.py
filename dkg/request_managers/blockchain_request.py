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
from typing import Type, Dict, Any

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


@dataclass
class KnowledgeCollectionResult:
    knowledge_collection_id: int
    receipt: Dict[str, Any]


@dataclass
class AllowanceResult:
    allowance_increased: bool
    allowance_gap: int


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

    key_is_operational_wallet = ContractCall(
        contract="IdentityStorage",
        function="keyHasPurpose",
        args={"identityId": int, "_key": Address, "_purpose": int},
    )

    time_until_next_epoch = ContractCall(
        contract="Chronos",
        function="timeUntilNextEpoch",
        args={},
    )

    epoch_length = ContractCall(
        contract="Chronos",
        function="epochLength",
        args={},
    )

    get_stake_weighted_average_ask = ContractCall(
        contract="AskStorage",
        function="getStakeWeightedAverageAsk",
        args={},
    )

    allowance = ContractCall(
        contract="Token",
        function="allowance",
        args={"owner": Address, "spender": Address},
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

    burn_knowledge_assets_tokens = ContractTransaction(
        contract="KnowledgeCollectionStorage",
        function="burnKnowledgeAssetsTokens",
        args={"id": int, "from": Address, "tokenIds": list[int]},
    )
    # extend_asset_storing_period = ContractTransaction(
    #     contract="ContentAsset",
    #     function="extendAssetStoringPeriod",
    #     args={"tokenId": int, "epochsNumber": int, "tokenAmount": int},
    # )

    transfer_asset = ContractTransaction(
        contract="KnowledgeCollectionStorage",
        function="safeTransferFrom",
        args={"from": Address, "to": Address, "id": int, "amount": int, "data": bytes},
    )

    is_knowledge_collection_owner = ContractCall(
        contract="KnowledgeCollectionStorage",
        function="isKnowledgeCollectionOwner",
        args={"owner": Address, "id": int},
    )

    # Identity
    get_identity_id = ContractCall(
        contract="IdentityStorage",
        function="getIdentityId",
        args={"operational": Address},
    )

    # Paranets
    register_paranet = ContractTransaction(
        contract="Paranet",
        function="registerParanet",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "paranetName": str,
            "paranetDescription": str,
            "nodesAccessPolicy": int,
            "minersAccessPolicy": int,
        },
    )

    is_paranet_operator = ContractCall(
        contract="ParanetNeuroIncentivesPool",
        function="isParanetOperator",
        args={"addr": Address},
    )

    add_paranet_curated_nodes = ContractTransaction(
        contract="Paranet",
        function="addParanetCuratedNodes",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "identityIds": list[int],
        },
    )

    remove_paranet_curated_nodes = ContractTransaction(
        contract="Paranet",
        function="removeParanetCuratedNodes",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "identityIds": list[int],
        },
    )

    request_paranet_curated_node_access = ContractTransaction(
        contract="Paranet",
        function="requestParanetCuratedNodeAccess",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
        },
    )

    approve_curated_node = ContractTransaction(
        contract="Paranet",
        function="approveCuratedNode",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "identityId": int,
        },
    )

    reject_curated_node = ContractTransaction(
        contract="Paranet",
        function="rejectCuratedNode",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "identityId": int,
        },
    )

    get_curated_nodes = ContractCall(
        contract="ParanetsRegistry",
        function="getCuratedNodes",
        args={"paranetId": HexStr},
    )

    add_paranet_curated_miners = ContractTransaction(
        contract="Paranet",
        function="addParanetCuratedMiners",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "minerAddresses": list[Address],
        },
    )

    remove_paranet_curated_miners = ContractTransaction(
        contract="Paranet",
        function="removeParanetCuratedMiners",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "minerAddresses": list[Address],
        },
    )

    request_paranet_curated_miner_access = ContractTransaction(
        contract="Paranet",
        function="requestParanetCuratedMinerAccess",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
        },
    )

    approve_curated_miner = ContractTransaction(
        contract="Paranet",
        function="approveCuratedMiner",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "minerAddress": Address,
        },
    )

    reject_curated_miner = ContractTransaction(
        contract="Paranet",
        function="rejectCuratedMiner",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "minerAddress": Address,
        },
    )

    get_knowledge_miners = ContractCall(
        contract="ParanetsRegistry",
        function="getKnowledgeMiners",
        args={"paranetId": HexStr},
    )

    add_paranet_services = ContractTransaction(
        contract="Paranet",
        function="addParanetServices",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "paranetKATokenId": int,
            "services": dict[str, Address | int],
        },
    )
    register_paranet_service = ContractTransaction(
        contract="Paranet",
        function="registerParanetService",
        args={
            "paranetServiceKCStorageContract": Address,
            "paranetServiceKCTokenId": int,
            "paranetServiceKATokenId": int,
            "paranetServiceName": str,
            "paranetServiceDescription": str,
            "paranetServiceAddresses": list[Address],
        },
    )
    submit_knowledge_collection = ContractTransaction(
        contract="Paranet",
        function="submitKnowledgeCollection",
        args={
            "paranetKCStorageContract": Address,
            "paranetKnowledgeCollectionTokenId": int,
            "paranetKnowledgeAssetTokenId": int,
            "knowledgeCollectionStorageContract": Address,
            "knowledgeCollectionTokenId": int,
        },
    )

    deploy_neuro_incentives_pool = ContractTransaction(
        contract="ParanetIncentivesPoolFactory",
        function="deployNeuroIncentivesPool",
        args={
            "isNativeReward": bool,
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
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

    is_knowledge_miner_registered = ContractCall(
        contract="ParanetsRegistry",
        function="isKnowledgeMinerRegistered",
        args={
            "paranetId": HexStr,
            "knowledgeMinerAddress": Address,
        },
    )
    is_proposal_voter = ContractCall(
        contract="ParanetNeuroIncentivesPool",
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

    create_knowledge_collection = ContractTransaction(
        contract="KnowledgeCollection",
        function="createKnowledgeCollection",
        args={
            "publishOperationId": str,
            "merkleRoot": bytes,
            "knowledgeAssetsAmount": int,
            "byteSize": int,
            "epochs": int,
            "tokenAmount": int,
            "isImmutable": bool,
            "paymaster": Address,
            "publisherNodeIdentityId": int,
            "publisherNodeR": bytes,
            "publisherNodeVS": bytes,
            "identityIds": list[int],
            "r": list[bytes],
            "vs": list[bytes],
        },
    )

    mint_knowledge_collection = ContractTransaction(
        contract="Paranet",
        function="mintKnowledgeCollection",
        args={
            "paranetKCStorageContract": Address,
            "paranetKCTokenId": int,
            "knowledgeAssetArgs": dict,
        },
    )
