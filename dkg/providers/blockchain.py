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

import json
import os
from collections import namedtuple
from functools import wraps
from pathlib import Path
from typing import Any, Type

import requests
from dkg.constants import BLOCKCHAINS, DEFAULT_GAS_PRICE_GWEI
from dkg.exceptions import (
    AccountMissing,
    EnvironmentNotSupported,
    NetworkNotSupported,
    RPCURINotDefined,
)
from dkg.types import URI, Address, DataHexStr, Environment, Wei
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract import Contract
from web3.contract.contract import ContractFunction
from web3.logs import DISCARD
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.types import ABI, ABIFunction, TxReceipt


class BlockchainProvider:
    CONTRACTS_METADATA_DIR = Path(__file__).parents[1] / "data/interfaces"

    def __init__(
        self,
        environment: Environment,
        blockchain_id: str,
        rpc_uri: URI | None = None,
        private_key: DataHexStr | None = None,
        gas_price: Wei | None = None,
        verify: bool = True,
    ):
        if environment not in BLOCKCHAINS.keys():
            raise EnvironmentNotSupported(f"Environment {environment} isn't supported!")

        self.environment = environment
        self.rpc_uri = rpc_uri
        self.blockchain_id = (
            blockchain_id
            if blockchain_id in BLOCKCHAINS[self.environment].keys()
            else None
        )

        if self.rpc_uri is None and self.blockchain_id is not None:
            self.blockchain_id = blockchain_id
            self.rpc_uri = self.rpc_uri or BLOCKCHAINS[self.environment][
                self.blockchain_id
            ].get("rpc", None)

        if self.rpc_uri is None:
            raise RPCURINotDefined(
                "No RPC URI provided for unrecognized "
                f"blockchain ID {self.blockchain_id}"
            )

        self.w3 = Web3(
            Web3.HTTPProvider(self.rpc_uri, request_kwargs={"verify": verify})
        )

        if self.blockchain_id is None:
            self.blockchain_id = f"{blockchain_id}:{self.w3.eth.chain_id}"
            if self.blockchain_id not in BLOCKCHAINS[self.environment]:
                raise NetworkNotSupported(
                    f"Network with blockchain ID {self.blockchain_id} isn't supported!"
                )

        self.gas_price = gas_price
        self.gas_price_oracle = BLOCKCHAINS[self.environment][self.blockchain_id].get(
            "gas_price_oracle",
            None,
        )

        self.abi = self._load_abi()
        self.output_named_tuples = self._generate_output_named_tuples()

        hub_address: Address = BLOCKCHAINS[self.environment][self.blockchain_id]["hub"]
        self.contracts: dict[str, Contract] = {
            "Hub": self.w3.eth.contract(
                address=hub_address,
                abi=self.abi["Hub"],
                decode_tuples=True,
            )
        }
        self._init_contracts()

        if (
            private_key is not None
            or (private_key_env := os.environ.get("PRIVATE_KEY", None)) is not None
        ):
            self.set_account(private_key or private_key_env)

    def make_json_rpc_request(self, endpoint: str, args: dict[str, Any] = {}) -> Any:
        web3_method = getattr(self.w3.eth, endpoint)

        if callable(web3_method):
            return web3_method(**args)
        else:
            return web3_method

    @staticmethod
    def handle_updated_contract(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            contract_name = kwargs.get("contract") or (args[0] if args else None)

            try:
                return func(self, *args, **kwargs)
            except Exception as err:
                if (
                    contract_name
                    and isinstance(contract_name, str)
                    and any(msg in str(err) for msg in ["revert", "VM Exception"])
                    and not self._check_contract_status(contract_name)
                ):
                    is_updated = self._update_contract_instance(contract_name)
                    if is_updated:
                        return func(self, *args, **kwargs)
                raise err

        return wrapper

    @handle_updated_contract
    def call_function(
        self,
        contract: str | dict[str, str],
        function: str,
        args: dict[str, Any] = {},
        state_changing: bool = False,
        gas_price: Wei | None = None,
        gas_limit: Wei | None = None,
    ) -> TxReceipt | Any:
        if isinstance(contract, str):
            contract_name = contract
            contract_instance = self.contracts[contract_name]
        else:
            contract_name = contract["name"]
            contract_instance = self.w3.eth.contract(
                address=contract["address"],
                abi=self.abi[contract_name],
                decode_tuples=True,
            )
            self.contracts[contract_name] = contract_instance

        contract_function: ContractFunction = getattr(
            contract_instance.functions, function
        )

        if not state_changing:
            result = contract_function(**args).call()
            if function in (
                output_named_tuples := self.output_named_tuples[contract_name]
            ):
                result = output_named_tuples[function](*result)
            return result
        else:
            if not hasattr(self, "account"):
                raise AccountMissing(
                    "State-changing transactions can be performed only with specified "
                    "account."
                )

            gas_price = self.gas_price or gas_price or self._get_network_gas_price()

            options = {
                "gasPrice": gas_price,
                "gas": gas_limit or contract_function(**args).estimate_gas(),
            }

            tx_hash = contract_function(**args).transact(options)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return tx_receipt

    def decode_logs_event(
        self, receipt: TxReceipt, contract_name: str, event_name: str
    ) -> Any:
        return (
            self.contracts[contract_name]
            .events[event_name]()
            .process_receipt(receipt, errors=DISCARD)
        )

    def set_account(self, private_key: DataHexStr):
        self.account: LocalAccount = self.w3.eth.account.from_key(private_key)
        self.w3.middleware_onion.add(
            construct_sign_and_send_raw_middleware(self.account)
        )
        self.w3.eth.default_account = self.account.address

    def _get_network_gas_price(self) -> Wei | None:
        if self.environment == "development":
            return None

        blockchain_name, _ = self.blockchain_id.split(":")

        default_gas_price = self.w3.to_wei(
            DEFAULT_GAS_PRICE_GWEI[blockchain_name], "gwei"
        )

        def fetch_gas_price(oracle_url: str) -> Wei | None:
            try:
                response = requests.get(oracle_url)
                response.raise_for_status()
                data: dict = response.json()

                if "result" in data:
                    return int(data["result"], 16)
                elif "average" in data:
                    return self.w3.to_wei(data["average"], "gwei")
                else:
                    return None
            except Exception:
                return None

        oracles = self.gas_price_oracle
        if oracles is not None:
            if isinstance(oracles, str):
                oracles = [oracles]

            for oracle_url in oracles:
                gas_price = fetch_gas_price(oracle_url)
                if gas_price is not None:
                    return gas_price

        return default_gas_price

    def _init_contracts(self):
        for contract in self.abi.keys():
            if contract == "Hub":
                continue

            self._update_contract_instance(contract)

    def _update_contract_instance(self, contract: str) -> bool:
        if (
            self.contracts["Hub"].functions.isContract(contractName=contract).call()
            or self.contracts["Hub"]
            .functions.isAssetStorage(assetStorageName=contract)
            .call()
        ):
            self.contracts[contract] = self.w3.eth.contract(
                address=(
                    self.contracts["Hub"].functions.getContractAddress(contract).call()
                    if not contract.endswith("AssetStorage")
                    else self.contracts["Hub"]
                    .functions.getAssetStorageAddress(contract)
                    .call()
                ),
                abi=self.abi[contract],
                decode_tuples=True,
            )
            return True
        return False

    def _check_contract_status(self, contract: str) -> bool:
        try:
            return self.call_function(contract, "status")
        except Exception:
            return False

    def _generate_output_named_tuples(self) -> dict[str, dict[str, Type[tuple]]]:
        def generate_output_namedtuple(function_abi: ABIFunction) -> Type[tuple] | None:
            output_names = [output["name"] for output in function_abi["outputs"]]
            if all(name != "" for name in output_names):
                return namedtuple(f"{function_abi['name']}Result", output_names)
            return None

        output_named_tuples = {}
        for contract_name, contract_abi in self.abi.items():
            output_named_tuples[contract_name] = {}
            for item in contract_abi:
                if (item["type"] != "function") or not item["outputs"]:
                    continue
                elif item["name"] in output_named_tuples[contract_name]:
                    continue
                named_tuple = generate_output_namedtuple(item)
                if named_tuple is not None:
                    output_named_tuples[contract_name][item["name"]] = named_tuple

        return output_named_tuples

    def _load_abi(self) -> ABI:
        abi = {}

        for contract_metadata in self.CONTRACTS_METADATA_DIR.glob("*.json"):
            with open(contract_metadata, "r") as metadata_json:
                abi[contract_metadata.stem] = json.load(metadata_json)

        return abi
