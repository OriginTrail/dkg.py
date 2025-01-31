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

import os
import asyncio
from dotenv import load_dotenv
from functools import wraps
from typing import Any

import aiohttp
from dkg.constants import BLOCKCHAINS
from dkg.exceptions import (
    AccountMissing,
    NetworkNotSupported,
)
from dkg.types import URI, Address, Environment, Wei
from web3.contract import Contract
from web3.contract.contract import ContractFunction
from web3.types import TxReceipt
from web3.providers import AsyncHTTPProvider
from web3 import AsyncWeb3
from dkg.providers.blockchain.base_blockchain import BaseBlockchainProvider


class AsyncBlockchainProvider(BaseBlockchainProvider):
    def __init__(
        self,
        environment: Environment,
        blockchain_id: str,
        rpc_uri: URI | None = None,
        gas_price: Wei | None = None,
        verify: bool = True,
    ):
        super().__init__(environment, blockchain_id, rpc_uri, gas_price)

        ssl_context = None if verify else False
        self.w3 = AsyncWeb3(
            AsyncHTTPProvider(self.rpc_uri, request_kwargs={"ssl": ssl_context})
        )

        if self.blockchain_id is None:
            self.blockchain_id = f"{blockchain_id}:{self.w3.eth.chain_id}"
            if self.blockchain_id not in BLOCKCHAINS[self.environment]:
                raise NetworkNotSupported(
                    f"Network with blockchain ID {self.blockchain_id} isn't supported!"
                )

        self.gas_price_oracle = BLOCKCHAINS[self.environment][self.blockchain_id].get(
            "gas_price_oracle",
            None,
        )

        hub_address: Address = BLOCKCHAINS[self.environment][self.blockchain_id]["hub"]
        self.contracts: dict[str, Contract] = {
            "Hub": self.w3.eth.contract(
                address=hub_address,
                abi=self.abi["Hub"],
                decode_tuples=True,
            )
        }

        self.contracts_initialized = False

        load_dotenv()
        if private_key := os.environ.get("PRIVATE_KEY"):
            self.set_account(private_key)

    async def ensure_contracts_initialized(self):
        if not self.contracts_initialized:
            await self._init_contracts()
            self.contracts_initialized = True

    async def make_json_rpc_request(
        self, endpoint: str, args: dict[str, Any] = {}
    ) -> Any:
        web3_method = getattr(self.w3.eth, endpoint)

        if callable(web3_method):
            return await web3_method(**args)
        else:
            return web3_method

    @staticmethod
    def handle_updated_contract(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            contract_name = kwargs.get("contract") or (args[0] if args else None)

            try:
                return await func(self, *args, **kwargs)
            except Exception as err:
                if (
                    contract_name
                    and isinstance(contract_name, str)
                    and any(msg in str(err) for msg in ["revert", "VM Exception"])
                    and not await self._check_contract_status(contract_name)
                ):
                    is_updated = await self._update_contract_instance(contract_name)
                    if is_updated:
                        return await func(self, *args, **kwargs)
                raise err

        return wrapper

    @handle_updated_contract
    async def call_function(
        self,
        contract: str | dict[str, str],
        function: str,
        args: dict[str, Any] = {},
        state_changing: bool = False,
        gas_price: Wei | None = None,
        gas_limit: Wei | None = None,
    ) -> TxReceipt | Any:
        await self.ensure_contracts_initialized()
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
            result = await contract_function(**args).call()
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

            options = {
                "gas": gas_limit or await contract_function(**args).estimate_gas(),
            }

            gas_price = (
                self.gas_price or gas_price or await self._get_network_gas_price()
            )

            if gas_price is not None:
                options["gasPrice"] = gas_price

            tx_hash = await contract_function(**args).transact(options)
            tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return tx_receipt

    async def _get_network_gas_price(self) -> Wei | None:
        if self.environment == "development":
            return None

        async def fetch_gas_price(oracle_url: str) -> Wei | None:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(oracle_url) as response:
                        response.raise_for_status()
                        data: dict = await response.json()

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
                gas_price = await fetch_gas_price(oracle_url)
                if gas_price is not None:
                    return gas_price

        return None

    async def _init_contracts(self):
        init_tasks = []
        for contract in self.abi.keys():
            if contract == "Hub":
                continue
            init_tasks.append(self._update_contract_instance(contract))
        await asyncio.gather(*init_tasks)

    async def _update_contract_instance(self, contract: str) -> bool:
        [is_contract, is_storage] = await asyncio.gather(
            self.contracts["Hub"].functions.isContract(contractName=contract).call(),
            self.contracts["Hub"]
            .functions.isAssetStorage(assetStorageName=contract)
            .call(),
        )
        if is_contract or is_storage:
            self.contracts[contract] = self.w3.eth.contract(
                address=(
                    await self.contracts["Hub"]
                    .functions.getAssetStorageAddress(contract)
                    .call()
                    if contract.endswith("AssetStorage")
                    or contract.endswith("CollectionStorage")
                    else await self.contracts["Hub"]
                    .functions.getContractAddress(contract)
                    .call()
                ),
                abi=self.abi[contract],
                decode_tuples=True,
            )
            return True
        return False

    async def _check_contract_status(self, contract: str) -> bool:
        try:
            return await self.call_function(contract, "status")
        except Exception:
            return False

    def set_incentives_pool(self, incentives_pool_address: Address):
        # Update contract address if different
        if (
            self.contracts.get("ParanetNeuroIncentivesPool") is None
            or self.contracts["ParanetNeuroIncentivesPool"].address
            != incentives_pool_address
        ):
            # Create new contract instance
            self.contracts["ParanetNeuroIncentivesPool"] = self.w3.eth.contract(
                address=incentives_pool_address,
                abi=self.abi["ParanetNeuroIncentivesPool"],
                decode_tuples=True,
            )
