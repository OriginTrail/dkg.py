from dataclasses import dataclass, field
from typing import Type

from dkg.types import Address, Wei


@dataclass
class ContractInteraction:
    """
    A dataclass representing a contract interaction with the required fields.

    Attributes:
        contract (str): The name of the contract to interact with.
        function (str): The name of the function to call.
        args (dict[str, Type]): A dictionary containing the function's arguments with
        their names as keys and types as values.
    """

    contract: str
    function: str
    args: dict[str, Type] = field(default_factory=dict)


@dataclass
class ContractTransaction(ContractInteraction):
    """
    A dataclass inheriting from ContractInteraction representing a contract transaction
    with additional fields.

    Attributes:
        gas_price (Wei | None): The gas price for the transaction (optional).
        gas_limit (Wei | None): The gas limit for the transaction (optional).
    """

    gas_price: Wei | None = None
    gas_limit: Wei | None = None


@dataclass
class ContractCall(ContractInteraction):
    """
    A dataclass inheriting from ContractInteraction representing a contract call
    without any additional fields.
    """

    pass


class BlockchainRequest:
    """
    A class containing predefined contract calls and transactions for the blockchain.

    Attributes:
        get_contract_address (ContractCall): A contract call to get the address of a
        specified contract.
        get_asset_storage_address (ContractCall): A contract call to get the address of
        a specified asset storage.
        increase_allowance (ContractTransaction): A contract transaction to increase
        the allowance of a specified spender.
        decrease_allowance (ContractTransaction): A contract transaction to decrease
        the allowance of a specified spender.
        create_asset (ContractTransaction): A contract transaction to create a new
        asset.
        get_latest_assertion_id (ContractCall): A contract call to get the latest
        assertion ID for a specified token ID.
        owner_of (ContractCall): A contract call to get the owner of a specified token
        ID.
    """

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

    increase_allowance = ContractTransaction(
        contract="Token",
        function="increaseAllowance",
        args={"spender": Address, "addedValue": Wei},
        #  gas_price=
        #  gas_limit=
    )
    decrease_allowance = ContractTransaction(
        contract="Token",
        function="decreaseAllowance",
        args={"spender": Address, "subtractedValue": Wei},
        #  gas_price=
        #  gas_limit=
    )

    create_asset = ContractTransaction(
        contract="ContentAsset",
        function="createAsset",
        args={"args": dict[str, bytes | int | Wei | bool]},
        #  gas_price=
        #  gas_limit=
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
