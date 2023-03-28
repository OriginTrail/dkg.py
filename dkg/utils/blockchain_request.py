from dataclasses import dataclass, field
from typing import Type
from dkg.types import Address, Wei


@dataclass
class ContractInteraction:
    contract: str
    function: str
    args: dict[str, Type] = field(default_factory=dict)


@dataclass
class ContractTransaction(ContractInteraction):
    gas_price: Wei | None = None
    gas_limit: Wei | None = None


@dataclass
class ContractCall(ContractInteraction):
    pass


class BlockchainRequest:
    get_contract_address = ContractCall(
        contract='Hub',
        function='getContractAddress',
        args={'contractName': str},
    )
    get_asset_storage_address = ContractCall(
        contract='Hub',
        function='getAssetStorageAddress',
        args={'assetStorageName': str},
    )

    increase_allowance = ContractTransaction(
        contract='Token',
        function='increaseAllowance',
        args={'spender': Address, 'addedValue': Wei},
        #  gas_price=
        #  gas_limit=
    )
    decrease_allowance = ContractTransaction(
        contract='Token',
        function='decreaseAllowance',
        args={'spender': Address, 'subtractedValue': Wei},
        #  gas_price=
        #  gas_limit=
    )

    create_asset = ContractTransaction(
        contract='ContentAsset',
        function='createAsset',
        args={'args': dict[str, bytes | int | Wei | bool]},
        #  gas_price=
        #  gas_limit=
    )
    get_latest_assertion_id = ContractCall(
        contract='ContentAssetStorage',
        function='getLatestAssertionId',
        args={'tokenId': int},
    )
    owner_of = ContractCall(
        contract='ContentAssetStorage',
        function='ownerOf',
        args={'tokenId': int},
    )
