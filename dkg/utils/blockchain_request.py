from dataclasses import dataclass, field
from typing import Type

from dkg.types import Address, HexStr, Wei


@dataclass
class JSONRPCRequest:
    endpoint: str
    args: dict[str, Type] = field(default_factory=dict)


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
        args={"agreementId": HexStr},
    )

    get_assertion_size = ContractCall(
        contract="AssertionStorage",
        function="getAssertionSize",
        args={"assertionId": HexStr},
    )
