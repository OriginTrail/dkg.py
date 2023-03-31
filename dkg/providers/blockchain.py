import json
from pathlib import Path
from typing import Any

from dkg.exceptions import AccountMissing, NetworkNotSupported
from dkg.types import URI, Address, DataHexStr, Wei
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.contract import Contract
from web3.contract.contract import ContractFunction
from web3.logs import DISCARD
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.types import TxReceipt


class BlockchainProvider:
    """
    A class for interacting with the blockchain using Web3.

    Attributes:
        w3 (Web3): A Web3 instance for making requests to the blockchain.
        abi (dict): A dictionary containing the contract ABIs.
        contracts (dict[str, Contract]): A dictionary containing contract instances.
    """

    CONTRACTS_METADATA_DIR = Path(__file__).parents[1] / "data/interfaces"
    SUPPORTED_NETWORKS = {
        2043: "otp_mainnet",
        2160: "otp_devnet",
        20430: "otp_testnet",
        31337: "hardhat",
    }
    GAS_BUFFER = 1.2  # 20% gas buffer for estimateGas()

    def __init__(
        self, rpc_uri: URI, hub_address: Address, private_key: DataHexStr | None = None
    ):
        """
        Initialize a BlockchainProvider instance with the specified RPC URI, hub
        address, and private key.

        Args:
            rpc_uri (URI): The URI of the RPC endpoint to connect to.
            hub_address (Address): The address of the hub contract.
            private_key (DataHexStr | None, optional): The private key for the account.
            Defaults to None.
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_uri))

        if self.chain_id not in self.SUPPORTED_NETWORKS.keys():
            raise NetworkNotSupported(
                f"Network with chain ID {self.chain_id} isn't supported!"
            )

        self.abi = self._load_abi()
        self.contracts: dict[str, Contract] = {
            "Hub": self.w3.eth.contract(
                address=hub_address,
                abi=self.abi["Hub"],
            )
        }
        self._init_contracts()

        if private_key is not None:
            self.set_account(private_key)

    @property
    def chain_id(self):
        """Returns the chain ID of the connected blockchain."""
        return self.w3.eth.chain_id

    @property
    def chain_name(self):
        """Returns the name of the connected blockchain."""
        chain_name = self.SUPPORTED_NETWORKS[self.w3.eth.chain_id]
        return "otp" if chain_name.startswith("otp") else chain_name

    def call_function(
        self,
        contract: str,
        function: str,
        args: dict[str, Any],
        state_changing: bool = False,
        gas_price: Wei | None = None,
        gas_limit: Wei | None = None,
    ) -> TxReceipt | Any:
        """
        Call a contract function on the blockchain.

        Args:
            contract (str): The name of the contract.
            function (str): The name of the function to call.
            args (dict[str, Any]): A dictionary of arguments for the function.
            state_changing (bool, optional): Whether the function call changes the
            state. Defaults to False.
            gas_price (Wei | None, optional): The gas price for the transaction.
            Defaults to None.
            gas_limit (Wei | None, optional): The gas limit for the transaction.
            Defaults to None.

        Returns:
            TxReceipt | Any: The transaction receipt if state-changing, or the return
            value of the function call.
        """
        contract_instance = self.contracts[contract]
        contract_function: ContractFunction = getattr(
            contract_instance.functions, function
        )

        if not state_changing:
            return contract_function(**args).call()
        else:
            if not hasattr(self, "account"):
                raise AccountMissing(
                    "State-changing transactions can be performed only with specified"
                    " account."
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
        """
        Decode logs from a transaction receipt for a specific contract and event.

        Args:
            receipt (TxReceipt): The transaction receipt.
            contract_name (str): The name of the contract.
            event_name (str): The name of the event.

        Returns:
            Any: The decoded logs data.
        """
        return (
            self.contracts[contract_name]
            .events[event_name]()
            .process_receipt(receipt, errors=DISCARD)
        )

    def set_account(self, private_key: DataHexStr):
        """
        Set the account for the blockchain provider using a private key.

        Args:
            private_key (DataHexStr): The private key for the account.
        """
        self.account: LocalAccount = self.w3.eth.account.from_key(private_key)
        self.w3.middleware_onion.add(
            construct_sign_and_send_raw_middleware(self.account)
        )
        self.w3.eth.default_account = self.account.address

    def _init_contracts(self):
        """Initialize contract instances for the blockchain provider."""
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

    def _load_abi(self):
        """Load contract ABIs from JSON files and return them as a dictionary."""
        abi = {}

        for contract_metadata in self.CONTRACTS_METADATA_DIR.glob("*.json"):
            with open(contract_metadata, "r") as metadata_json:
                abi[contract_metadata.stem] = json.load(metadata_json)

        return abi
