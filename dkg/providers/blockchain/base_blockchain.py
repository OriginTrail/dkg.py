import json
from collections import namedtuple
from pathlib import Path
from typing import Any, Type

from dkg.constants import BLOCKCHAINS
from dkg.exceptions import (
    EnvironmentNotSupported,
    RPCURINotDefined,
)
from dkg.types import URI, DataHexStr, Environment, Wei
from eth_account.signers.local import LocalAccount
from eth_typing import ABI, ABIFunction
from web3.logs import DISCARD
from web3.middleware import SignAndSendRawMiddlewareBuilder
from web3.types import TxReceipt


class BaseBlockchainProvider:
    CONTRACTS_METADATA_DIR = Path(__file__).parents[2] / "data/interfaces"

    def __init__(
        self,
        environment: Environment,
        blockchain_id: str,
        rpc_uri: URI | None = None,
        gas_price: Wei | None = None,
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

        self.gas_price = gas_price

        self.abi = self._load_abi()
        self.output_named_tuples = self._generate_output_named_tuples()

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
        self.w3.middleware_onion.inject(
            SignAndSendRawMiddlewareBuilder.build(private_key),
            layer=0,
        )
        self.w3.eth.default_account = self.account.address

    def set_incentives_pool(self):
        raise NotImplementedError("This method has to be implemented in the subclass")
