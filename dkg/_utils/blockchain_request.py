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
        args={'address': Address, 'token_amount': Wei},
        #  gas_price=
        #  gas_limit=
    )
    decrease_allowance = ContractTransaction(
        contract='Token',
        function='decreaseAllowance',
        args={'address': Address, 'token_amount': Wei},
        #  gas_price=
        #  gas_limit=
    )

    create_asset = ContractTransaction(
        contract='ContentAsset',
        function='createAsset',
        args={
            'assertion_id': DataHexStr,
            'size': int,
            'triples_number': int,
            'chunks_number': int,
            'epochs_number': int,
            'token_amount': Wei,
            'score_function_id': int,
            'immutable': bool,
        },
        #  gas_price=
        #  gas_limit=
    )
    owner_of = ContractCall(
        contract='ContentAsset',
        function='ownerOf',
        args={'token_id': int},
    )
