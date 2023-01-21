from pathlib import Path
import yaml
import json
from web3 import Web3

DEFAULT_CONFIG = Path(__file__).parents[2] / 'data/default-config.yaml'
CONTRACTS_METADATA_DIR = Path(__file__).parents[2] / 'metadata'


class BlockchainService:
    def __init__(self, network: str, config_path: Path = DEFAULT_CONFIG):
        self.network = network
        self.config = self._load_config(config_path)
        self.provider = Web3(Web3.HTTPProvider(self.config['rpc']))
        self.abi = self._load_abi()
        self.hub = self.provider.eth.contract(
            address=self.config['hub_address'],
            abi=self.abi['Hub'],
        )
        self.contracts = self._init_contracts()
        self.asset_contracts = self._init_contracts(assets=True)

    def _init_contracts(self, assets=False):
        return {
            contract: self.provider.eth.contract(
                address=(
                    self.hub.functions.getContractAddress(
                        contract if contract != 'ERC20Token' else 'Token'
                    ).call()
                    if not assets
                    else
                    self.hub.functions.getAssetStorageAddress(contract).call()
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

    def _load_config(self, config_path: Path):
        with open(config_path, "r") as yamlfile:
            config = yaml.load(yamlfile, Loader=yaml.FullLoader)

        return config[self.network]
