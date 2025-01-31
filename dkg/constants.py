from enum import Enum, auto, StrEnum
from dkg.types import AutoStrEnumUpperCase

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

DEFAULT_CANON_ALGORITHM = "URDNA2015"
DEFAULT_RDF_FORMAT = "application/n-quads"

PRIVATE_ASSERTION_PREDICATE = (
    "https://ontology.origintrail.io/dkg/1.0#privateMerkleRoot"
)

PRIVATE_HASH_SUBJECT_PREFIX = "https://ontology.origintrail.io/dkg/1.0#metadata-hash:"

PRIVATE_RESOURCE_PREDICATE = (
    "https://ontology.origintrail.io/dkg/1.0#representsPrivateResource"
)

CHUNK_BYTE_SIZE = 32

MAX_FILE_SIZE = 10000000


class DefaultParameters(Enum):
    ENVIRONMENT: str = "mainnet"
    PORT: int = 8900
    FREQUENCY: int = 5
    MAX_NUMBER_OF_RETRIES: int = 5
    HASH_FUNCTION_ID: int = 1
    MIN_NUMBER_OF_FINALIZATION_CONFIRMATION: int = 3
    IMMUTABLE: bool = False
    VALIDATE: bool = True
    OUTPUT_FORMAT: str = "JSON-LD"
    STATE: None = None
    INCLUDE_METADATA: bool = False
    CONTENT_TYPE: str = "all"
    HANDLE_NOT_MINED_ERROR: bool = False
    SIMULATE_TXS: bool = False
    FORCE_REPLACE_TXS: bool = False
    GAS_LIMIT_MULTIPLIER: int = 1
    PARANET_UAL: None = None
    GET_SUBJECT_UAL: bool = False


class OutputTypes(StrEnum):
    NQUADS = "N-QUADS"
    JSONLD = "JSON-LD"


class Environments(StrEnum):
    DEVELOPMENT = "development"
    DEVNET = "devnet"
    TESTNET = "testnet"
    MAINNET = "mainnet"


class BlockchainIds(StrEnum):
    HARDHAT_1 = "hardhat1:31337"
    HARDHAT_2 = "hardhat2:31337"
    BASE_DEVNET = "base:84532"
    GNOSIS_DEVNET = "gnosis:10200"
    NEUROWEB_DEVNET = "otp:2160"
    BASE_TESTNET = "base:84532"
    GNOSIS_TESTNET = "gnosis:10200"
    NEUROWEB_TESTNET = "otp:20430"
    BASE_MAINNET = "base:8453"
    GNOSIS_MAINNET = "gnosis:100"
    NEUROWEB_MAINNET = "otp:2043"


class OperationStatuses(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
BLOCKCHAINS = {
    "development": {
        "hardhat1:31337": {
            "hub": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
            "rpc": "http://localhost:8545",
        },
        "hardhat2:31337": {
            "hub": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
            "rpc": "http://localhost:9545",
        },
    },
    "devnet": {
        "base:84532": {
            "hub": "0xE043daF4cC8ae2c720ef95fc82574a37a429c40A",
            "rpc": "https://sepolia.base.org",
        }
    },
    "testnet": {
        "base:84532": {
            "hub": "0xf21CE8f8b01548D97DCFb36869f1ccB0814a4e05",
            "rpc": "https://sepolia.base.org",
        },
        "gnosis:10200": {
            "hub": "0x2c08AC4B630c009F709521e56Ac385A6af70650f",
            "rpc": "https://rpc.chiadochain.net",
        },
        "otp:20430": {
            "hub": "0xd7d073b560412c6A7F33dD670d323D01061E5DEb",
            "rpc": "https://lofar-testnet.origin-trail.network",
        },
    },
    "mainnet": {
        "base:8453": {
            "hub": "0x99Aa571fD5e681c2D27ee08A7b7989DB02541d13",
            "rpc": "https://mainnet.base.org",
        },
        "gnosis:100": {
            "hub": "0x882D0BF07F956b1b94BBfe9E77F47c6fc7D4EC8f",
            "rpc": "https://rpc.gnosischain.com/",
        },
        "otp:2043": {
            "hub": "0x0957e25BD33034948abc28204ddA54b6E1142D6F",
            "rpc": "https://astrosat-parachain-rpc.origin-trail.network",
        },
    },
}

DEFAULT_PROXIMITY_SCORE_FUNCTIONS_PAIR_IDS = {
    "development": {"hardhat1:31337": 2, "hardhat2:31337": 2, "otp:2043": 2},
    "devnet": {
        "otp:2160": 2,
        "gnosis:10200": 2,
        "base:84532": 2,
    },
    "testnet": {
        "otp:20430": 2,
        "gnosis:10200": 2,
        "base:84532": 2,
    },
    "mainnet": {
        "otp:2043": 2,
        "gnosis:100": 2,
        "base:8453": 2,
    },
}


class Operations(Enum):
    PUBLISH = "publish"
    GET = "get"
    QUERY = "query"
    PUBLISH_PARANET = "publishParanet"
    FINALITY = "finality"


class Status(AutoStrEnumUpperCase):
    ERROR = auto()
    NOT_FINALIZED = auto()
    FINALIZED = auto()
    NETWORK_ERROR = auto()


class ErrorType(AutoStrEnumUpperCase):
    DKG_CLIENT_ERROR = auto()
