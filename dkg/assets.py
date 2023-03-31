import json
from typing import Literal

from pyld import jsonld
from web3 import Web3
from web3.exceptions import ContractLogicError

from dkg.dataclasses import NodeResponseDict
from dkg.exceptions import InvalidAsset, OperationNotFinished
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import JSONLD, UAL, Address, HexStr
from dkg.utils.blockchain_request import BlockchainRequest
from dkg.utils.decorators import retry
from dkg.utils.merkle import MerkleTree, hash_assertion_with_indexes
from dkg.utils.node_request import NodeRequest, StoreTypes, validate_operation_status
from dkg.utils.rdf import normalize_dataset
from dkg.utils.ual import format_ual, parse_ual


class ContentAsset(Module):
    """
    A class to represent the ContentAsset component in the Decentralized Knowledge Graph
    (DKG) system.
    This class inherits from the Module class and provides methods for creating, querying,
    and managing content assets.

    Attributes:
        manager (DefaultRequestManager): An instance of DefaultRequestManager for managing
        requests to the ContentAsset.
        HASH_FUNCTION_ID (int): The default hash function identifier.
        SCORE_FUNCTION_ID (int): The default score function identifier.
    """

    HASH_FUNCTION_ID = 1
    SCORE_FUNCTION_ID = 1

    def __init__(self, manager: DefaultRequestManager):
        """
        Initializes a ContentAsset object with the given request manager.

        Args:
            manager (DefaultRequestManager): An instance of DefaultRequestManager for
            managing requests to the ContentAsset.
        """
        self.manager = manager

    _get_bid_suggestion = Method(NodeRequest.bid_suggestion)
    _local_store = Method(NodeRequest.local_store)
    _publish = Method(NodeRequest.publish)

    _get_contract_address = Method(BlockchainRequest.get_contract_address)
    _get_asset_storage_address = Method(BlockchainRequest.get_asset_storage_address)
    _increase_allowance = Method(BlockchainRequest.increase_allowance)
    _decrease_allowance = Method(BlockchainRequest.decrease_allowance)
    _create = Method(BlockchainRequest.create_asset)

    def create(
        self,
        content: dict[Literal["public", "private"], JSONLD],
        epochs_number: int,
        token_amount: int | None = None,
        immutable: bool = False,
        content_type: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
    ) -> dict[str, UAL | HexStr | dict[str, str]]:
        """
        Creates a new content asset in the DKG system with the given content and parameters.

        Args:
            content (dict): A dictionary containing the public and private content to be
            stored in the asset.
            epochs_number (int): The number of epochs for which the content asset should be
            stored.
            token_amount (int | None): The number of tokens to be used for the asset. If
            None, the system will suggest an amount.
            immutable (bool): Whether the asset should be immutable. Default is False.
            content_type (Literal['JSON-LD', 'N-Quads']): The format of the content data.
            Default is 'JSON-LD'.

        Returns:
            dict: A dictionary containing the UAL, public assertion ID, and operation details
            for the created asset.
        """
        public_graph = {"@graph": []}
        assertions: list[dict[str, str | Address | JSONLD]] = []

        if content["public"]:
            public_graph["@graph"].append(content["public"])

        if content["private"]:
            public_graph["@graph"].append(content["private"])

            private_assertion = normalize_dataset(content["private"], content_type)
            private_assertion_id = (
                "0x"
                + MerkleTree(
                    hash_assertion_with_indexes(private_assertion),
                    sort_pairs=True,
                ).root
            )

        public_assertion = normalize_dataset(public_graph, content_type)
        public_assertion_id = (
            "0x"
            + MerkleTree(
                hash_assertion_with_indexes(public_assertion),
                sort_pairs=True,
            ).root
        )
        public_assertion_size = len(
            json.dumps(public_assertion, separators=(",", ":")).encode("utf-8")
        )
        public_assertion_triples_number = len(public_assertion)
        # TODO: Change when chunking introduced
        public_assertion_chunks_number = len(public_assertion)

        chain_name = self.manager.blockchain_provider.chain_name
        content_asset_storage_address = self._get_asset_storage_address(
            "ContentAssetStorage"
        )

        if token_amount is None:
            token_amount = int(
                self._get_bid_suggestion(
                    chain_name,
                    epochs_number,
                    public_assertion_size,
                    content_asset_storage_address,
                    public_assertion_id,
                    self.HASH_FUNCTION_ID,
                )["bidSuggestion"]
            )

        service_agreement_v1_address = str(
            self._get_contract_address("ServiceAgreementV1")
        )
        self._increase_allowance(service_agreement_v1_address, token_amount)

        try:
            receipt = self._create(
                {
                    "assertionId": Web3.to_bytes(hexstr=public_assertion_id),
                    "size": public_assertion_size,
                    "triplesNumber": public_assertion_triples_number,
                    "chunksNumber": public_assertion_chunks_number,
                    "tokenAmount": token_amount,
                    "epochsNumber": epochs_number,
                    "scoreFunctionId": self.SCORE_FUNCTION_ID,
                    "immutable_": immutable,
                }
            )
        except ContractLogicError as err:
            self._decrease_allowance(service_agreement_v1_address, token_amount)
            raise err

        events = self.manager.blockchain_provider.decode_logs_event(
            receipt,
            "ContentAsset",
            "AssetMinted",
        )
        token_id = events[0].args["tokenId"]

        assertions = [
            {
                "blockchain": chain_name,
                "contract": content_asset_storage_address,
                "tokenId": token_id,
                "assertionId": private_assertion_id,
                "assertion": private_assertion,
                "storeType": StoreTypes.TRIPLE.value,
            }
        ]

        if content["private"]:
            assertions.append(
                {
                    "blockchain": chain_name,
                    "contract": content_asset_storage_address,
                    "tokenId": token_id,
                    "assertionId": public_assertion_id,
                    "assertion": public_assertion,
                    "storeType": StoreTypes.TRIPLE.value,
                }
            )

        operation_id = self._local_store(assertions)["operationId"]
        self.get_operation_result(operation_id, "local-store")

        operation_id = self._publish(
            public_assertion_id,
            public_assertion,
            chain_name,
            content_asset_storage_address,
            token_id,
            self.HASH_FUNCTION_ID,
        )["operationId"]
        operation_result = self.get_operation_result(operation_id, "publish")

        return {
            "UAL": format_ual(chain_name, content_asset_storage_address, token_id),
            "publicAssertionId": public_assertion_id,
            "operation": {
                "operationId": operation_id,
                "status": operation_result["status"],
            },
        }

    _get = Method(NodeRequest.get)
    _get_latest_assertion_id = Method(BlockchainRequest.get_latest_assertion_id)

    def get(
        self, ual: UAL, validate: bool = False
    ) -> dict[str, HexStr | list[JSONLD] | dict[str, str]]:
        """
        Retrieves a content asset from the DKG system by its UAL.

        Args:
            ual (UAL): The UAL of the content asset to retrieve.
            validate (bool): Whether to validate the asset against the latest assertion ID.
            Default is False.

        Returns:
            dict: A dictionary containing the assertion ID, assertion data, and operation
            details for the retrieved asset.

        Raises:
            InvalidAsset: If the asset is invalid when validation is enabled.
        """
        operation_id: NodeResponseDict = self._get(ual, hashFunctionId=1)["operationId"]

        @retry(catch=OperationNotFinished, max_retries=5, base_delay=1, backoff=2)
        def get_operation_result() -> NodeResponseDict:
            operation_result = self._get_operation_result(
                operation="get",
                operation_id=operation_id,
            )

            validate_operation_status(operation_result)

        operation_result = get_operation_result()
        assertion = operation_result["data"]["assertion"]

        token_id = parse_ual(ual)["tokenId"]
        latest_assertion_id = Web3.to_hex(self._get_latest_assertion_id(token_id))

        if validate:
            merkle_tree = MerkleTree(
                hash_assertion_with_indexes(assertion), sort_pairs=True
            )
            root = "0x" + merkle_tree.root
            if root != latest_assertion_id:
                raise InvalidAsset(
                    f"Latest assertionId: {latest_assertion_id}. "
                    f"Merkle Tree Root: {root}"
                )

        assertion_json_ld: list[JSONLD] = jsonld.from_rdf(
            "\n".join(assertion),
            {"algorithm": "URDNA2015", "format": "application/n-quads"},
        )

        return {
            "assertionId": latest_assertion_id,
            "assertion": assertion_json_ld,
            "operation": {
                "operation_id": operation_id,
                "status": operation_result["status"],
            },
        }

    _owner = Method(BlockchainRequest.owner_of)

    def owner(self, token_id: int) -> Address:
        """
        Retrieves the owner's address of a content asset by its token ID.

        Args:
            token_id (int): The token ID of the content asset.

        Returns:
            Address: The address of the content asset's owner.
        """
        return self._owner(token_id)

    _get_operation_result = Method(NodeRequest.get_operation_result)

    @retry(catch=OperationNotFinished, max_retries=5, base_delay=1, backoff=2)
    def get_operation_result(
        self, operation_id: str, operation: str
    ) -> NodeResponseDict:
        """
        Retrieves the result of a previously executed operation on the content asset,
        retrying up to 5 times with exponential backoff if the operation is not yet finished.

        Args:
            operation_id (str): The identifier of the operation.
            operation (str): The type of operation.

        Returns:
            NodeResponseDict: A dictionary containing the operation result.

        Raises:
            OperationNotFinished: If the operation is not finished after the maximum number
            of retries.
        """
        operation_result = self._get_operation_result(
            operation_id=operation_id,
            operation=operation,
        )

        validate_operation_status(operation_result)

        return operation_result


class Assets(Module):
    """
    A class to represent the Assets component in the Decentralized Knowledge Graph (DKG) system.
    This class inherits from the Module class and provides methods for managing different
    types of assets.

    Attributes:
        ContentAsset (ContentAsset): An instance of the ContentAsset class for managing content
        assets in the DKG system.
    """

    ContentAsset: ContentAsset
