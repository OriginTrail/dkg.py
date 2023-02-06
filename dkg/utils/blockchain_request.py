from dataclasses import dataclass, field
from typing import Type
from dkg.types import Address, Wei, DataHexStr


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
        args={'spender': Address, 'substractedValue': Wei},
        #  gas_price=
        #  gas_limit=
    )

    create_asset = ContractTransaction(
        contract='ContentAsset',
        function='createAsset',
        args={
            'assertionId': DataHexStr,
            'size': int,
            'triplesNumber': int,
            'chunksNumber': int,
            'epochsNumber': int,
            'tokenAmount': Wei,
            'scoreFunctionId': int,
            'immutable_': bool,
        },
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
