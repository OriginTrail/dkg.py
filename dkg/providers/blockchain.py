from pathlib import Path
import json
from web3 import Web3
from dkg.types import URI, Address, Wei, DataHexStr
from dkg.exceptions import AccountMissing
from eth_account.signers.local import LocalAccount
from web3.contract import Contract, ContractFunction
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.types import TxReceipt
from typing import Any

CONTRACTS_METADATA_DIR = Path(__file__).parents[1] / 'data/interfaces'


class BlockchainProvider:
    def __init__(self, rpc_uri: URI, hub_address: Address, private_key: DataHexStr | None = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_uri))

        self.abi = self._load_abi()
        self.hub: Contract = self.w3.eth.contract(
            address=hub_address,
            abi=self.abi['Hub'],
        )
        self.contracts = self._init_contracts()

        if private_key is not None:
            self.set_account(private_key)

    def call_function(
        self,
        contract: str,
        function: str,
        args: dict[str, Any],
        state_changing: bool = False,
        gas_price: Wei | None = None,
        gas_limit: Wei | None = None,
    ) -> TxReceipt | Any:
        contract_instance = self.contracts[contract]
        contract_function: ContractFunction = getattr(contract_instance.functions, function)

        if not state_changing:
            return contract_function(**args).call()
        else:
            if not hasattr(self, "account"):
                raise AccountMissing(
                    "State-changing transactions can be performed only with specified account."
                )

            nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
            gas_price = gas_price if gas_price is not None else self.w3.eth.gas_price

            options = {
                'nonce': nonce,
                'gasPrice': gas_price
            }

            if gas_limit is not None:
                options.update({'gas': gas_limit})

            tx_hash = contract_function(**args).transact(options)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return tx_receipt

    def set_account(self, private_key: DataHexStr):
        self.account: LocalAccount = self.w3.eth.account.from_key(private_key)
        self.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(self.account))
        self.w3.eth.default_account = self.account.address

    def _init_contracts(self):
        return {
            contract: self.w3.eth.contract(
                address=(
                    self.hub.functions.getContractAddress(
                        contract if contract != 'ERC20Token' else 'Token'
                    ).call() if not contract.endswith('AssetStorage')
                    else self.hub.functions.getAssetStorageAddress(contract).call()
                ),
                abi=self.abi[contract],
            )
            for contract in self.abi.keys() if contract != 'Hub'
        }

    def _load_abi(self):
        abi = {}

        for contract_metadata in CONTRACTS_METADATA_DIR.glob('*.json'):
            with open(contract_metadata, 'r') as metadata_json:
                abi[contract_metadata.stem] = json.load(metadata_json)['abi']

        return abi

    def _load_contract_metadata(self, name):
        if name == "Token":
            name = "ERC20Token"

        with open(f'{CONTRACTS_METADATA_DIR}/{name}.json', 'r') as contract_metadata:
            contract_metadata_json = json.load(contract_metadata)

        return contract_metadata_json
