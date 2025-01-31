from dkg.method import Method
from dkg.request_managers.blockchain_request import BlockchainRequest


class BaseBlockchainService:
    # Common methods shared between sync and async services
    _get_contract_address = Method(BlockchainRequest.get_contract_address)
    _get_current_allowance = Method(BlockchainRequest.allowance)
    _increase_allowance = Method(BlockchainRequest.increase_allowance)
    _decrease_allowance = Method(BlockchainRequest.decrease_allowance)
    _create_knowledge_collection = Method(BlockchainRequest.create_knowledge_collection)
    _mint_knowledge_collection = Method(BlockchainRequest.mint_knowledge_collection)
    _get_asset_storage_address = Method(BlockchainRequest.get_asset_storage_address)
    _key_is_operational_wallet = Method(BlockchainRequest.key_is_operational_wallet)
    _time_until_next_epoch = Method(BlockchainRequest.time_until_next_epoch)
    _epoch_length = Method(BlockchainRequest.epoch_length)
    _get_stake_weighted_average_ask = Method(
        BlockchainRequest.get_stake_weighted_average_ask
    )
    _get_block = Method(BlockchainRequest.get_block)
    _register_paranet = Method(BlockchainRequest.register_paranet)
    _submit_knowledge_collection = Method(BlockchainRequest.submit_knowledge_collection)
    _register_paranet_service = Method(BlockchainRequest.register_paranet_service)
    _add_paranet_services = Method(BlockchainRequest.add_paranet_services)
    _deploy_neuro_incentives_pool = Method(
        BlockchainRequest.deploy_neuro_incentives_pool
    )
    _get_incentives_pool_address = Method(BlockchainRequest.get_incentives_pool_address)
    _is_knowledge_miner_registered = Method(
        BlockchainRequest.is_knowledge_miner_registered
    )
    _is_knowledge_collection_owner = Method(
        BlockchainRequest.is_knowledge_collection_owner
    )
    _is_paranet_operator = Method(BlockchainRequest.is_paranet_operator)
    _is_proposal_voter = Method(BlockchainRequest.is_proposal_voter)
    _burn_knowledge_assets_tokens = Method(
        BlockchainRequest.burn_knowledge_assets_tokens
    )
    _transfer_asset = Method(BlockchainRequest.transfer_asset)
