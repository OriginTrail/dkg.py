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

import math
import re
from typing import Literal, Type

from pyld import jsonld
from web3 import Web3
from web3.constants import HASH_ZERO
from web3.exceptions import ContractLogicError

from dkg.constants import BLOCKCHAINS, PRIVATE_ASSERTION_PREDICATE
from dkg.dataclasses import (
    KnowledgeAssetContentVisibility,
    KnowledgeAssetEnumStates,
    NodeResponseDict,
)
from dkg.exceptions import (
    DatasetOutputFormatNotSupported,
    InvalidKnowledgeAsset,
    InvalidStateOption,
    InvalidTokenAmount,
    MissingKnowledgeAssetState,
    OperationNotFinished,
)
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import JSONLD, UAL, Address, AgreementData, HexStr, NQuads, Wei
from dkg.utils.blockchain_request import BlockchainRequest
from dkg.utils.decorators import retry
from dkg.utils.merkle import MerkleTree, hash_assertion_with_indexes
from dkg.utils.metadata import (
    generate_agreement_id,
    generate_assertion_metadata,
    generate_keyword,
)
from dkg.utils.node_request import NodeRequest, StoreTypes, validate_operation_status
from dkg.utils.rdf import normalize_dataset
from dkg.utils.ual import format_ual, parse_ual


class ContentAsset(Module):
    DEFAULT_HASH_FUNCTION_ID = 1
    DEFAULT_SCORE_FUNCTION_ID = 1
    PRIVATE_HISTORICAL_REPOSITORY = "privateHistory"
    PRIVATE_CURRENT_REPOSITORY = "privateCurrent"

    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _get_current_allowance = Method(BlockchainRequest.allowance)

    def get_current_allowance(self, spender: Address) -> int:
        return int(
            self._get_current_allowance(
                self.manager.blockchain_provider.account.address, spender
            )
        )

    _increase_allowance = Method(BlockchainRequest.increase_allowance)

    def increase_allowance(self, spender: Address, token_amount: Wei) -> int:
        current_allowance = self.get_current_allowance(spender)
        missing_allowance = 0
        if current_allowance < token_amount:
            missing_allowance = token_amount - current_allowance
            self._increase_allowance(spender, token_amount)

        return missing_allowance

    _decrease_allowance = Method(BlockchainRequest.decrease_allowance)

    def decrease_allowance(self, spender: Address, token_amount: Wei) -> int:
        current_allowance = self.get_current_allowance(spender)

        if current_allowance - token_amount < 0:
            self._decrease_allowance(spender, token_amount - current_allowance)

        return token_amount - current_allowance

    _chain_id = Method(BlockchainRequest.chain_id)

    _get_contract_address = Method(BlockchainRequest.get_contract_address)
    _get_asset_storage_address = Method(BlockchainRequest.get_asset_storage_address)
    _create = Method(BlockchainRequest.create_asset)

    _get_bid_suggestion = Method(NodeRequest.bid_suggestion)
    _local_store = Method(NodeRequest.local_store)
    _publish = Method(NodeRequest.publish)

    def create(
        self,
        content: dict[Literal["public", "private"], JSONLD],
        epochs_number: int,
        token_amount: Wei | None = None,
        immutable: bool = False,
        content_type: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
    ) -> dict[str, HexStr | dict[str, str]]:
        assertions = self._process_content(content, content_type)

        chain_name = BLOCKCHAINS[self._chain_id()]["name"]
        content_asset_storage_address = self._get_asset_storage_address(
            "ContentAssetStorage"
        )

        if token_amount is None:
            token_amount = int(
                self._get_bid_suggestion(
                    chain_name,
                    epochs_number,
                    assertions["public"]["size"],
                    content_asset_storage_address,
                    assertions["public"]["id"],
                    self.DEFAULT_HASH_FUNCTION_ID,
                )["bidSuggestion"]
            )

        service_agreement_v1_address = str(
            self._get_contract_address("ServiceAgreementV1")
        )
        allowance_increased = (
            self.increase_allowance(service_agreement_v1_address, token_amount) > 0
        )

        # self.increase_allowance(service_agreement_v1_address, token_amount)

        try:
            receipt = self._create(
                {
                    "assertionId": Web3.to_bytes(hexstr=assertions["public"]["id"]),
                    "size": assertions["public"]["size"],
                    "triplesNumber": assertions["public"]["triples_number"],
                    "chunksNumber": assertions["public"]["chunks_number"],
                    "tokenAmount": token_amount,
                    "epochsNumber": epochs_number,
                    "scoreFunctionId": self.DEFAULT_SCORE_FUNCTION_ID,
                    "immutable_": immutable,
                }
            )
        except ContractLogicError as err:
            if allowance_increased:
                self.decrease_allowance(service_agreement_v1_address, token_amount)
            raise err

        events = self.manager.blockchain_provider.decode_logs_event(
            receipt,
            "ContentAsset",
            "AssetMinted",
        )
        token_id = events[0].args["tokenId"]

        assertions_list = [
            {
                "blockchain": chain_name,
                "contract": content_asset_storage_address,
                "tokenId": token_id,
                "assertionId": assertions["public"]["id"],
                "assertion": assertions["public"]["content"],
                "storeType": StoreTypes.TRIPLE.value,
            }
        ]

        if content.get("private", None):
            assertions_list.append(
                {
                    "blockchain": chain_name,
                    "contract": content_asset_storage_address,
                    "tokenId": token_id,
                    "assertionId": assertions["private"]["id"],
                    "assertion": assertions["private"]["content"],
                    "storeType": StoreTypes.TRIPLE.value,
                }
            )

        operation_id = self._local_store(assertions_list)["operationId"]
        self.get_operation_result(operation_id, "local-store")

        operation_id = self._publish(
            assertions["public"]["id"],
            assertions["public"]["content"],
            chain_name,
            content_asset_storage_address,
            token_id,
            self.DEFAULT_HASH_FUNCTION_ID,
        )["operationId"]
        operation_result = self.get_operation_result(operation_id, "publish")

        return {
            "UAL": format_ual(chain_name, content_asset_storage_address, token_id),
            "publicAssertionId": assertions["public"]["id"],
            "operation": {
                "operationId": operation_id,
                "status": operation_result["status"],
            },
        }

    _transfer = Method(BlockchainRequest.transfer_asset)

    def transfer(
        self,
        ual: UAL,
        new_owner: Address,
    ) -> dict[str, UAL | Address | dict[str, str]]:
        token_id = parse_ual(ual)["token_id"]

        self._transfer(
            self.manager.blockchain_provider.account,
            new_owner,
            token_id,
        )

        return {
            "UAL": ual,
            "owner": new_owner,
            "operation": {"status": "COMPLETED"},
        }

    _update = Method(NodeRequest.update)

    _get_block = Method(BlockchainRequest.get_block)

    _get_service_agreement_data = Method(BlockchainRequest.get_service_agreement_data)
    _update_asset_state = Method(BlockchainRequest.update_asset_state)

    def update(
        self,
        ual: UAL,
        content: dict[Literal["public", "private"], JSONLD],
        token_amount: Wei | None = None,
        content_type: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
    ) -> dict[str, HexStr | dict[str, str]]:
        parsed_ual = parse_ual(ual)
        content_asset_storage_address, token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        assertions = self._process_content(content, content_type)

        chain_name = BLOCKCHAINS[self._chain_id()]["name"]

        if token_amount is None:
            agreement_id = self.get_agreement_id(
                content_asset_storage_address, token_id
            )
            # TODO: Dynamic types for namedtuples?
            agreement_data: Type[AgreementData] = self._get_service_agreement_data(
                agreement_id
            )

            timestamp_now = self._get_block("latest")["timestamp"]
            current_epoch = math.floor(
                (timestamp_now - agreement_data.startTime) / agreement_data.epochLength
            )
            epochs_left = agreement_data.epochsNumber - current_epoch

            token_amount = int(
                self._get_bid_suggestion(
                    chain_name,
                    epochs_left,
                    assertions["public"]["size"],
                    content_asset_storage_address,
                    assertions["public"]["id"],
                    self.DEFAULT_HASH_FUNCTION_ID,
                )["bidSuggestion"]
            )

            token_amount -= agreement_data.tokensInfo[0]
            token_amount = token_amount if token_amount > 0 else 0

        self._update_asset_state(
            token_id=token_id,
            assertion_id=assertions["public"]["id"],
            size=assertions["public"]["size"],
            triples_number=assertions["public"]["triples_number"],
            chunks_number=assertions["public"]["chunks_number"],
            update_token_amount=token_amount,
        )

        assertions_list = [
            {
                "blockchain": chain_name,
                "contract": content_asset_storage_address,
                "tokenId": token_id,
                "assertionId": assertions["public"]["id"],
                "assertion": assertions["public"]["content"],
                "storeType": StoreTypes.PENDING.value,
            }
        ]

        if content.get("private", None):
            assertions_list.append(
                {
                    "blockchain": chain_name,
                    "contract": content_asset_storage_address,
                    "tokenId": token_id,
                    "assertionId": assertions["private"]["id"],
                    "assertion": assertions["private"]["content"],
                    "storeType": StoreTypes.PENDING.value,
                }
            )

        operation_id = self._local_store(assertions_list)["operationId"]
        self.get_operation_result(operation_id, "local-store")

        operation_id = self._update(
            assertions["public"]["id"],
            assertions["public"]["content"],
            chain_name,
            content_asset_storage_address,
            token_id,
            self.DEFAULT_HASH_FUNCTION_ID,
        )["operationId"]
        operation_result = self.get_operation_result(operation_id, "update")

        return {
            "UAL": format_ual(chain_name, content_asset_storage_address, token_id),
            "publicAssertionId": assertions["public"]["id"],
            "operation": {
                "operationId": operation_id,
                "status": operation_result["status"],
            },
        }

    _cancel_update = Method(BlockchainRequest.cancel_asset_state_update)

    def cancel_update(self, ual: UAL) -> dict[str, UAL | dict[str, str]]:
        token_id = parse_ual(ual)["token_id"]

        self._cancel_update(token_id)

        return {
            "UAL": ual,
            "operation": {"status": "COMPLETED"},
        }

    _burn_asset = Method(BlockchainRequest.burn_asset)

    def burn(self, ual: UAL) -> dict[str, UAL | dict[str, str]]:
        token_id = parse_ual(ual)["token_id"]

        self._burn_asset(token_id)

        return {"UAL": ual, "operation": {"status": "COMPLETED"}}

    _get_assertion_ids = Method(BlockchainRequest.get_assertion_ids)
    _get_latest_assertion_id = Method(BlockchainRequest.get_latest_assertion_id)
    _get_unfinalized_state = Method(BlockchainRequest.get_unfinalized_state)

    _get = Method(NodeRequest.get)
    _query = Method(NodeRequest.query)

    def get(
        self,
        ual: UAL,
        state: str | HexStr | int = KnowledgeAssetEnumStates.LATEST.value,
        content_visibility: str = KnowledgeAssetContentVisibility.ALL.value,
        output_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
        validate: bool = True,
    ) -> dict[str, HexStr | list[JSONLD] | dict[str, str]]:
        state = (
            state.upper()
            if (isinstance(state, str) and not re.match(r"^0x[a-fA-F0-9]{64}$", state))
            else state
        )
        content_visibility = content_visibility.upper()
        output_format = output_format.upper()

        token_id = parse_ual(ual)["token_id"]

        def handle_latest_state(token_id: int) -> tuple[HexStr, bool]:
            unfinalized_state = Web3.to_hex(self._get_unfinalized_state(token_id))

            if unfinalized_state and unfinalized_state != HASH_ZERO:
                return unfinalized_state, False
            else:
                return handle_latest_finalized_state(token_id)

        def handle_latest_finalized_state(token_id: int) -> tuple[HexStr, bool]:
            return Web3.to_hex(self._get_latest_assertion_id(token_id)), True

        is_state_finalized = False

        match state:
            case KnowledgeAssetEnumStates.LATEST.value:
                public_assertion_id, is_state_finalized = handle_latest_state(token_id)

            case KnowledgeAssetEnumStates.LATEST_FINALIZED.value:
                public_assertion_id, is_state_finalized = handle_latest_finalized_state(
                    token_id
                )

            case _ if isinstance(state, int):
                assertion_ids = [
                    Web3.to_hex(assertion_id)
                    for assertion_id in self._get_assertion_ids(token_id)
                ]
                if 0 <= state < (states_number := len(assertion_ids)):
                    public_assertion_id = assertion_ids[state]

                    if state == states_number - 1:
                        is_state_finalized = True
                else:
                    raise InvalidStateOption(f"State index {state} is out of range.")

            case _ if isinstance(state, str) and re.match(
                r"^0x[a-fA-F0-9]{64}$", state
            ):
                assertion_ids = [
                    Web3.to_hex(assertion_id)
                    for assertion_id in self._get_assertion_ids(token_id)
                ]

                if state in assertion_ids:
                    public_assertion_id = state

                    if state == assertion_ids[-1]:
                        is_state_finalized = True
                else:
                    raise InvalidStateOption(
                        f"Given state hash: {state} is not a part of the KA."
                    )

            case _:
                raise InvalidStateOption(f"Invalid state option: {state}.")

        get_public_operation_id: NodeResponseDict = self._get(
            ual, public_assertion_id, hashFunctionId=1
        )["operationId"]

        get_public_operation_result = self.get_operation_result(
            get_public_operation_id, "get"
        )
        public_assertion = get_public_operation_result["data"].get("assertion", None)

        if public_assertion is None:
            raise MissingKnowledgeAssetState("Unable to find state on the network!")

        if validate:
            root = MerkleTree(
                hash_assertion_with_indexes(public_assertion), sort_pairs=True
            ).root
            if root != public_assertion_id:
                raise InvalidKnowledgeAsset(
                    f"State: {public_assertion_id}. " f"Merkle Tree Root: {root}"
                )

        result = {"operation": {}}
        if content_visibility != KnowledgeAssetContentVisibility.PRIVATE.value:
            formatted_public_assertion = public_assertion

            match output_format:
                case "NQUADS" | "N-QUADS":
                    formatted_public_assertion: list[JSONLD] = jsonld.from_rdf(
                        "\n".join(public_assertion),
                        {"algorithm": "URDNA2015", "format": "application/n-quads"},
                    )
                case "JSONLD" | "JSON-LD":
                    formatted_public_assertion = "\n".join(public_assertion)

                case _:
                    raise DatasetOutputFormatNotSupported(
                        f"{output_format} isn't supported!"
                    )

            if content_visibility == KnowledgeAssetContentVisibility.PUBLIC.value:
                result = {
                    **result,
                    "asertion": formatted_public_assertion,
                    "assertionId": public_assertion_id,
                }
            else:
                result["public"] = {
                    "assertion": formatted_public_assertion,
                    "assertionId": public_assertion_id,
                }

            result["operation"]["publicGet"] = {
                "operationId": get_public_operation_id,
                "status": get_public_operation_result["status"],
            }

        if content_visibility != KnowledgeAssetContentVisibility.PUBLIC.value:
            private_assertion_link_triples = list(
                filter(
                    lambda element: PRIVATE_ASSERTION_PREDICATE in element,
                    public_assertion,
                )
            )

            if private_assertion_link_triples:
                private_assertion_id = re.search(
                    r'"(.*?)"', private_assertion_link_triples[0]
                ).group(1)

                private_assertion = get_public_operation_result["data"].get(
                    "privateAssertion", None
                )

                query_private_operation_id: NodeResponseDict | None = None
                if private_assertion is None:
                    query = f"""
                    CONSTRUCT {{ ?s ?p ?o }}
                    WHERE {{
                        {{
                            GRAPH <assertion:{private_assertion_id}>
                            {{
                                ?s ?p ?o .
                            }}
                        }}
                    }}
                    """

                    query_private_operation_id = self._query(
                        query,
                        "CONSTRUCT",
                        self.PRIVATE_CURRENT_REPOSITORY
                        if is_state_finalized
                        else self.PRIVATE_HISTORICAL_REPOSITORY,
                    )["operationId"]

                    query_private_operation_result = self.get_operation_result(
                        query_private_operation_id, "query"
                    )

                    private_assertion = normalize_dataset(
                        query_private_operation_result["data"],
                        "N-Quads",
                    )

                    if validate:
                        root = MerkleTree(
                            hash_assertion_with_indexes(private_assertion),
                            sort_pairs=True,
                        ).root
                        if root != private_assertion_id:
                            raise InvalidKnowledgeAsset(
                                f"State: {private_assertion_id}. "
                                f"Merkle Tree Root: {root}"
                            )

                    match output_format:
                        case "NQUADS" | "N-QUADS":
                            formatted_private_assertion: list[JSONLD] = jsonld.from_rdf(
                                "\n".join(private_assertion),
                                {
                                    "algorithm": "URDNA2015",
                                    "format": "application/n-quads",
                                },
                            )
                        case "JSONLD" | "JSON-LD":
                            formatted_private_assertion = "\n".join(private_assertion)

                        case _:
                            raise DatasetOutputFormatNotSupported(
                                f"{output_format} isn't supported!"
                            )

                    if content_visibility == KnowledgeAssetContentVisibility.PRIVATE:
                        result = {
                            **result,
                            "assertion": formatted_private_assertion,
                            "assertionId": private_assertion_id,
                        }
                    else:
                        result["private"] = {
                            "assertion": formatted_private_assertion,
                            "assertionId": private_assertion_id,
                        }

                    if query_private_operation_id is not None:
                        result["operation"]["queryPrivate"] = {
                            "operationId": query_private_operation_id,
                            "status": query_private_operation_result["status"],
                        }

        return result

    _extend_storing_period = Method(BlockchainRequest.extend_asset_storing_period)

    def extend_storing_period(
        self,
        ual: UAL,
        additional_epochs: int,
        token_amount: Wei | None = None,
    ) -> dict[str, UAL | dict[str, str]]:
        parsed_ual = parse_ual(ual)
        content_asset_storage_address, token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        if token_amount is None:
            chain_name = BLOCKCHAINS[self._chain_id()]["name"]

            latest_finalized_state = self._get_latest_assertion_id(token_id)
            latest_finalized_state_size = self._get_assertion_size(
                latest_finalized_state
            )

            token_amount = int(
                self._get_bid_suggestion(
                    chain_name,
                    additional_epochs,
                    latest_finalized_state_size,
                    content_asset_storage_address,
                    latest_finalized_state,
                    self.DEFAULT_HASH_FUNCTION_ID,
                )["bidSuggestion"]
            )

        self._extend_storing_period(token_id, additional_epochs, token_amount)

        return {
            "UAL": ual,
            "operation": {"status": "COMPLETED"},
        }

    _get_assertion_size = Method(BlockchainRequest.get_assertion_size)
    _add_tokens = Method(BlockchainRequest.increase_asset_token_amount)

    def add_tokens(
        self,
        ual: UAL,
        token_amount: Wei | None = None,
    ) -> dict[str, UAL | dict[str, str]]:
        parsed_ual = parse_ual(ual)
        content_asset_storage_address, token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        if token_amount is None:
            chain_name = BLOCKCHAINS[self._chain_id()]["name"]

            agreement_id = self.get_agreement_id(
                content_asset_storage_address, token_id
            )
            # TODO: Dynamic types for namedtuples?
            agreement_data: Type[AgreementData] = self._get_service_agreement_data(
                agreement_id
            )

            timestamp_now = self._get_block("latest")["timestamp"]
            current_epoch = math.floor(
                (timestamp_now - agreement_data.startTime) / agreement_data.epochLength
            )
            epochs_left = agreement_data.epochsNumber - current_epoch

            latest_finalized_state = self._get_latest_assertion_id(token_id)
            latest_finalized_state_size = self._get_assertion_size(
                latest_finalized_state
            )

            token_amount = int(
                self._get_bid_suggestion(
                    chain_name,
                    epochs_left,
                    latest_finalized_state_size,
                    content_asset_storage_address,
                    latest_finalized_state,
                    self.DEFAULT_HASH_FUNCTION_ID,
                )["bidSuggestion"]
            ) - sum(agreement_data.tokensInfo)

            if token_amount <= 0:
                raise InvalidTokenAmount(
                    "Token amount is bigger than default suggested amount, "
                    "please specify exact token_amount if you still want to add "
                    "more tokens!"
                )

        self._add_tokens(token_id, token_amount)

        return {
            "UAL": ual,
            "operation": {"status": "COMPLETED"},
        }

    _add_update_tokens = Method(BlockchainRequest.increase_asset_update_token_amount)

    def add_update_tokens(
        self,
        ual: UAL,
        token_amount: Wei | None = None,
    ) -> dict[str, UAL | dict[str, str]]:
        parsed_ual = parse_ual(ual)
        content_asset_storage_address, token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        if token_amount is None:
            chain_name = BLOCKCHAINS[self._chain_id()]["name"]

            agreement_id = self.get_agreement_id(
                content_asset_storage_address, token_id
            )
            # TODO: Dynamic types for namedtuples?
            agreement_data: Type[AgreementData] = self._get_service_agreement_data(
                agreement_id
            )

            timestamp_now = self._get_block("latest")["timestamp"]
            current_epoch = math.floor(
                (timestamp_now - agreement_data.startTime) / agreement_data.epochLength
            )
            epochs_left = agreement_data.epochsNumber - current_epoch

            unfinalized_state = self._get_latest_assertion_id(token_id)
            unfinalized_state_size = self._get_assertion_size(unfinalized_state)

            token_amount = int(
                self._get_bid_suggestion(
                    chain_name,
                    epochs_left,
                    unfinalized_state_size,
                    content_asset_storage_address,
                    unfinalized_state,
                    self.DEFAULT_HASH_FUNCTION_ID,
                )["bidSuggestion"]
            ) - sum(agreement_data.tokensInfo)

            if token_amount <= 0:
                raise InvalidTokenAmount(
                    "Token amount is bigger than default suggested amount, "
                    "please specify exact token_amount if you still want to add "
                    "more update tokens!"
                )

        self._add_update_tokens(token_id, token_amount)

        return {
            "UAL": ual,
            "operation": {"status": "COMPLETED"},
        }

    _owner = Method(BlockchainRequest.owner_of)

    def get_owner(self, ual: UAL) -> Address:
        token_id = parse_ual(ual)["token_id"]

        return self._owner(token_id)

    def _process_content(
        self,
        content: dict[Literal["public", "private"], JSONLD],
        type: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
    ) -> dict[str, dict[str, HexStr | NQuads | int]]:
        public_graph = {"@graph": []}

        if content.get("public", None):
            public_graph["@graph"].append(content["public"])

        if content.get("private", None):
            private_assertion = normalize_dataset(content["private"], type)
            private_assertion_id = MerkleTree(
                hash_assertion_with_indexes(private_assertion),
                sort_pairs=True,
            ).root

            public_graph["@graph"].append(
                {PRIVATE_ASSERTION_PREDICATE: private_assertion_id}
            )

        public_assertion = normalize_dataset(public_graph, type)
        public_assertion_id = MerkleTree(
            hash_assertion_with_indexes(public_assertion),
            sort_pairs=True,
        ).root
        public_assertion_metadata = generate_assertion_metadata(public_assertion)

        return {
            "public": {
                "id": public_assertion_id,
                "content": public_assertion,
                **public_assertion_metadata,
            },
            "private": {
                "id": private_assertion_id,
                "content": private_assertion,
            }
            if content.get("private", None)
            else {},
        }

    _get_assertion_id_by_index = Method(BlockchainRequest.get_assertion_id_by_index)

    def get_agreement_id(self, contract_address: Address, token_id: int) -> HexStr:
        first_assertion_id = self._get_assertion_id_by_index(token_id, 0)
        keyword = generate_keyword(contract_address, first_assertion_id)
        return generate_agreement_id(contract_address, token_id, keyword)

    _get_operation_result = Method(NodeRequest.get_operation_result)

    @retry(catch=OperationNotFinished, max_retries=5, base_delay=1, backoff=2)
    def get_operation_result(
        self, operation_id: str, operation: str
    ) -> NodeResponseDict:
        operation_result = self._get_operation_result(
            operation_id=operation_id,
            operation=operation,
        )

        validate_operation_status(operation_result)

        return operation_result
