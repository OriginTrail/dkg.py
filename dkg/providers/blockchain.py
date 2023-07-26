import json
from collections import namedtuple
from pathlib import Path
from typing import Any, Type

from dkg.exceptions import AccountMissing, NetworkNotSupported
from dkg.types import URI, Address, DataHexStr, Wei
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract import Contract
from web3.contract.contract import ContractFunction
from web3.logs import DISCARD
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.types import ABI, ABIFunction, TxReceipt
from dkg.constants import BLOCKCHAINS

class BlockchainProvider:
    CONTRACTS_METADATA_DIR = Path(__file__).parents[1] / "data/interfaces"

    GAS_BUFFER = 1.2  # 20% gas buffer for estimateGas()

    def __init__(
        self,
        rpc_uri: URI,
        private_key: DataHexStr | None = None,
        verify: bool = True,
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_uri, request_kwargs={"verify": verify}))

        if (chain_id := self.w3.eth.chain_id) not in BLOCKCHAINS.keys():
            raise NetworkNotSupported(
                f"Network with chain ID {chain_id} isn't supported!"
            )
        hub_address: Address = BLOCKCHAINS[chain_id]["hubAddress"]

        self.abi = self._load_abi()
        self.output_named_tuples = self._generate_output_named_tuples()
        self.contracts: dict[str, Contract] = {
            "Hub": self.w3.eth.contract(
                address=hub_address,
                abi=self.abi["Hub"],
            )
        }
        self._init_contracts()

        if private_key is not None:
            self.set_account(private_key)

    def make_json_rpc_request(self, endpoint: str, args: dict[str, Any] = {}) -> Any:
        web3_method = getattr(self.w3.eth, endpoint)

        if callable(web3_method):
            return web3_method(**args)
        else:
            return web3_method

    def call_function(
        self,
        contract: str,
        function: str,
        args: dict[str, Any] = {},
        state_changing: bool = False,
        gas_price: Wei | None = None,
        gas_limit: Wei | None = None,
    ) -> TxReceipt | Any:
        contract_instance = self.contracts[contract]
        contract_function: ContractFunction = getattr(
            contract_instance.functions, function
        )

        if not state_changing:
            result = contract_function(**args).call()
            if function in (output_named_tuples := self.output_named_tuples[contract]):
                result = output_named_tuples[function](*result)
            return result
        else:
            if not hasattr(self, "account"):
                raise AccountMissing(
                    "State-changing transactions can be performed only with specified "
                    "account."
                )

            nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
            gas_price = gas_price if gas_price is not None else self.w3.eth.gas_price

            options = {"nonce": nonce, "gasPrice": gas_price}
            gas_estimate = contract_function(**args).estimate_gas(options)

            if gas_limit is None:
                options["gas"] = int(gas_estimate * self.GAS_BUFFER)
            else:
                options["gas"] = gas_limit

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

    def _init_contracts(self):
        for contract in self.abi.keys():
            if contract == "Hub":
                continue

            self.contracts[contract] = self.w3.eth.contract(
                address=(
                    self.contracts["Hub"]
                    .functions.getContractAddress(
                        contract if contract != "ERC20Token" else "Token"
                    )
                    .call()
                    if not contract.endswith("AssetStorage")
                    else self.contracts["Hub"]
                    .functions.getAssetStorageAddress(contract)
                    .call()
                ),
                abi=self.abi[contract],
            )

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
