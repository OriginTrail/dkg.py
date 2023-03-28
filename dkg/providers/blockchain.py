from pathlib import Path
import json
from web3 import Web3
from dkg.types import URI, Address, Wei, DataHexStr
from dkg.exceptions import AccountMissing, NetworkNotSupported
from eth_account.signers.local import LocalAccount
from web3.contract import Contract
from web3.contract.contract import ContractFunction
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.types import TxReceipt
from web3.logs import DISCARD
from typing import Any


class BlockchainProvider:
    CONTRACTS_METADATA_DIR = Path(__file__).parents[1] / 'data/interfaces'
    SUPPORTED_NETWORKS = {
        2043: 'otp_mainnet',
        2160: 'otp_devnet',
        20430: 'otp_testnet',
        31337: 'hardhat',
    }
    GAS_BUFFER = 1.2  # 20% gas buffer for estimateGas()

    def __init__(self, rpc_uri: URI, hub_address: Address, private_key: DataHexStr | None = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_uri))

        if self.chain_id not in self.SUPPORTED_NETWORKS.keys():
            raise NetworkNotSupported(f'Network with chain ID {self.chain_id} isn\'t supported!')

        self.abi = self._load_abi()
        self.contracts: dict[str, Contract] = {
            'Hub': self.w3.eth.contract(
                address=hub_address,
                abi=self.abi['Hub'],
            )
        }
        self._init_contracts()

        if private_key is not None:
            self.set_account(private_key)

    @property
    def chain_id(self):
        return self.w3.eth.chain_id

    @property
    def chain_name(self):
        chain_name = self.SUPPORTED_NETWORKS[self.w3.eth.chain_id]
        return 'otp' if chain_name.startswith('otp') else chain_name

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
            if not hasattr(self, 'account'):
                raise AccountMissing(
                    'State-changing transactions can be performed only with specified account.'
                )

            nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
            gas_price = gas_price if gas_price is not None else self.w3.eth.gas_price

            options = {
                'nonce': nonce,
                'gasPrice': gas_price
            }
            gas_estimate = contract_function(**args).estimate_gas(options)

            if gas_limit is None:
                options['gas'] = int(gas_estimate * self.GAS_BUFFER)
            else:
                options['gas'] = gas_limit

            tx_hash = contract_function(**args).transact(options)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return tx_receipt

    def decode_logs_event(self, receipt: TxReceipt, contract_name: str, event_name: str) -> Any:
        return (
            self.contracts[contract_name]
                .events[event_name]()
                .process_receipt(receipt, errors=DISCARD)
        )

    def set_account(self, private_key: DataHexStr):
        self.account: LocalAccount = self.w3.eth.account.from_key(private_key)
        self.w3.middleware_onion.add(construct_sign_and_send_raw_middleware(self.account))
        self.w3.eth.default_account = self.account.address

    def _init_contracts(self):
        for contract in self.abi.keys():
            if contract == 'Hub':
                continue

            self.contracts[contract] = self.w3.eth.contract(
                address=(
                    self.contracts['Hub'].functions.getContractAddress(
                        contract if contract != 'ERC20Token' else 'Token'
                    ).call() if not contract.endswith('AssetStorage')
                    else self.contracts['Hub'].functions.getAssetStorageAddress(contract).call()
                ),
                abi=self.abi[contract],
            )

    def _load_abi(self):
        abi = {}

        for contract_metadata in self.CONTRACTS_METADATA_DIR.glob('*.json'):
            with open(contract_metadata, 'r') as metadata_json:
                abi[contract_metadata.stem] = json.load(metadata_json)

        return abi
