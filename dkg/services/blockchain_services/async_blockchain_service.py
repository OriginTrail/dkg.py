from dkg.modules.async_module import AsyncModule
from dkg.managers.async_manager import AsyncRequestManager
from dkg.constants import ZERO_ADDRESS
from web3 import Web3
from typing import Optional
from dkg.types import Address, HexStr
from dkg.request_managers.blockchain_request import (
    KnowledgeCollectionResult,
    AllowanceResult,
)
from dkg.dataclasses import ParanetIncentivizationType
from dkg.services.blockchain_services.base_blockchain_service import (
    BaseBlockchainService,
)


class AsyncBlockchainService(AsyncModule, BaseBlockchainService):
    def __init__(self, manager: AsyncRequestManager):
        self.manager = manager

    async def decrease_knowledge_collection_allowance(
        self,
        allowance_gap: int,
    ):
        knowledge_collection_address = await self._get_contract_address(
            "KnowledgeCollection"
        )
        await self._decrease_allowance(knowledge_collection_address, allowance_gap)

    async def increase_knowledge_collection_allowance(
        self,
        sender: str,
        token_amount: str,
    ) -> AllowanceResult:
        """
        Increases the allowance for knowledge collection if necessary.

        Args:
            sender: The address of the sender
            token_amount: The amount of tokens to check/increase allowance for

        Returns:
            AllowanceResult containing whether allowance was increased and the gap
        """
        knowledge_collection_address = await self._get_contract_address(
            "KnowledgeCollection"
        )

        allowance = await self._get_current_allowance(
            sender, knowledge_collection_address
        )
        allowance_gap = int(token_amount) - int(allowance)

        if allowance_gap > 0:
            await self._increase_allowance(knowledge_collection_address, allowance_gap)

            return AllowanceResult(
                allowance_increased=True, allowance_gap=allowance_gap
            )

        return AllowanceResult(allowance_increased=False, allowance_gap=allowance_gap)

    async def create_knowledge_collection(
        self,
        request: dict,
        paranet_ka_contract: Optional[Address] = None,
        paranet_token_id: Optional[int] = None,
    ) -> KnowledgeCollectionResult:
        """
        Creates a knowledge collection on the blockchain.

        Args:
            request: dict containing all collection parameters
            paranet_ka_contract: Optional paranet contract address
            paranet_token_id: Optional paranet token ID
            blockchain: Blockchain configuration

        Returns:
            KnowledgeCollectionResult containing collection ID and transaction receipt

        Raises:
            BlockchainError: If the collection creation fails
        """
        sender = self.manager.blockchain_provider.account.address
        allowance_increased = False
        allowance_gap = 0

        try:
            # Handle allowance
            if request.get("paymaster") and request.get("paymaster") != ZERO_ADDRESS:
                pass
            else:
                allowance_result = await self.increase_knowledge_collection_allowance(
                    sender=sender,
                    token_amount=request.get("tokenAmount"),
                )
                allowance_increased = allowance_result.allowance_increased
                allowance_gap = allowance_result.allowance_gap

            if not paranet_ka_contract and not paranet_token_id:
                receipt = await self._create_knowledge_collection(
                    request.get("publishOperationId"),
                    Web3.to_bytes(hexstr=request.get("merkleRoot")),
                    request.get("knowledgeAssetsAmount"),
                    request.get("byteSize"),
                    request.get("epochs"),
                    request.get("tokenAmount"),
                    request.get("isImmutable"),
                    request.get("paymaster"),
                    request.get("publisherNodeIdentityId"),
                    Web3.to_bytes(hexstr=request.get("publisherNodeR")),
                    Web3.to_bytes(hexstr=request.get("publisherNodeVS")),
                    request.get("identityIds"),
                    [Web3.to_bytes(hexstr=x) for x in request.get("r")],
                    [Web3.to_bytes(hexstr=x) for x in request.get("vs")],
                )
            else:
                receipt = await self._mint_knowledge_collection(
                    paranet_ka_contract,
                    paranet_token_id,
                    list(request.values()),
                )

            event_data = self.manager.blockchain_provider.decode_logs_event(
                receipt=receipt,
                contract_name="KnowledgeCollectionStorage",
                event_name="KnowledgeCollectionCreated",
            )
            collection_id = (
                int(getattr(event_data[0].get("args", {}), "id", None))
                if event_data
                else None
            )

            return KnowledgeCollectionResult(
                knowledge_collection_id=collection_id, receipt=receipt
            )

        except Exception as e:
            if allowance_increased:
                await self.decrease_knowledge_collection_allowance(allowance_gap)
            raise e

    async def get_asset_storage_address(self, asset_storage_name: str) -> Address:
        return await self._get_asset_storage_address(asset_storage_name)

    async def key_is_operational_wallet(
        self, identity_id: int, key: Address, purpose: int
    ) -> bool:
        return await self._key_is_operational_wallet(identity_id, key, purpose)

    async def time_until_next_epoch(self) -> int:
        return await self._time_until_next_epoch()

    async def epoch_length(self) -> int:
        return await self._epoch_length()

    async def get_stake_weighted_average_ask(self) -> int:
        return await self._get_stake_weighted_average_ask()

    async def get_block(self, block_identifier: str | int):
        return await self._get_block(block_identifier)

    async def register_paranet(
        self,
        knowledge_collection_storage: str | Address,
        knowledge_collection_token_id: int,
        knowledge_asset_token_id: int,
        name: str,
        description: str,
        paranet_nodes_access_policy: int,
        paranet_miners_access_policy: int,
    ):
        return await self._register_paranet(
            knowledge_collection_storage,
            knowledge_collection_token_id,
            knowledge_asset_token_id,
            name,
            description,
            paranet_nodes_access_policy,
            paranet_miners_access_policy,
        )

    async def submit_knowledge_collection(
        self,
        paranet_knowledge_collection_storage: str | Address,
        paranet_knowledge_collection_token_id: int,
        paranet_knowledge_asset_token_id: int,
        knowledge_collection_storage: str | Address,
        knowledge_collection_token_id: int,
    ):
        return await self._submit_knowledge_collection(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            paranet_knowledge_asset_token_id,
            knowledge_collection_storage,
            knowledge_collection_token_id,
        )

    async def register_paranet_service(
        self,
        knowledge_collection_storage: str | Address,
        knowledge_collection_token_id: int,
        knowledge_asset_token_id: int,
        paranet_service_name: str,
        paranet_service_description: str,
        paranet_service_addresses: list[Address],
    ):
        return await self._register_paranet_service(
            knowledge_collection_storage,
            knowledge_collection_token_id,
            knowledge_asset_token_id,
            paranet_service_name,
            paranet_service_description,
            paranet_service_addresses,
        )

    async def add_paranet_services(
        self,
        paranet_knowledge_collection_storage: str | Address,
        paranet_knowledge_collection_token_id: int,
        paranet_knowledge_asset_token_id: int,
        services: list,
    ):
        return await self._add_paranet_services(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            paranet_knowledge_asset_token_id,
            services,
        )

    async def deploy_neuro_incentives_pool(
        self,
        is_native_reward: bool,
        paranet_knowledge_collection_storage: str | Address,
        paranet_knowledge_collection_token_id: int,
        paranet_knowledge_asset_token_id: int,
        trac_to_neuro_emission_multiplier: float,
        paranet_operator_reward_percentage: float,
        paranet_incentivization_proposal_voters_reward_percentage: float,
    ):
        return await self._deploy_neuro_incentives_pool(
            is_native_reward,
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            paranet_knowledge_asset_token_id,
            trac_to_neuro_emission_multiplier,
            paranet_operator_reward_percentage,
            paranet_incentivization_proposal_voters_reward_percentage,
        )

    async def get_incentives_pool_address(
        self, paranet_id: HexStr, incentives_pool_type: ParanetIncentivizationType
    ):
        return await self._get_incentives_pool_address(paranet_id, incentives_pool_type)

    async def is_knowledge_miner_registered(self, paranet_id: HexStr, address: Address):
        return await self._is_knowledge_miner_registered(paranet_id, address)

    async def is_knowledge_collection_owner(self, owner: Address, id: int):
        return await self._is_knowledge_collection_owner(owner, id)

    async def is_paranet_operator(self, operator_address: Address):
        return await self._is_paranet_operator(operator_address)

    def set_incentives_pool(self, incentives_pool_address: Address):
        self.manager.blockchain_provider.set_incentives_pool(incentives_pool_address)

    async def is_proposal_voter(self, address: Address):
        return await self._is_proposal_voter(address)

    async def burn_knowledge_assets_tokens(
        self, id: int, from_: Address, token_ids: list[int]
    ):
        return await self._burn_knowledge_assets_tokens(id, from_, token_ids)

    async def transfer_asset(self, from_: Address, to: Address, token_id: int):
        return await self._transfer_asset(
            from_, to, token_id, 1, Web3.to_bytes(hexstr="0x")
        )
