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

PRIVATE_ASSERTION_PREDICATE = (
    "https://ontology.origintrail.io/dkg/1.0#privateAssertionID"
)

BLOCKCHAINS = {
    "development": {
        "hardhat1:31337":  {
            "hub": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
            "rpc": "http://localhost:8545",
        },
        "hardhat2:31337":  {
            "hub": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
            "rpc": "http://localhost:9545",
        },
    },
    "devnet": {
        "base:84532": {
            "hub": "0xaA849CAC4FA86f6b7484503f3c7a314772AED6d4",
            "rpc": "https://sepolia.base.org",
        }
    },
    "testnet": {
        "base:84532": {
            "hub": "0xCca0eA14540588A09c85cD6A6Fc53eA3A7010692",
            "rpc": "https://sepolia.base.org",
        }
    },
    "mainnet": {},
}

DEFAULT_GAS_PRICE_GWEI = {
    "otp": 1,
    "gnosis": 20,
    "base": 20,
}

DEFAULT_HASH_FUNCTION_ID = 1
DEFAULT_PROXIMITY_SCORE_FUNCTIONS_PAIR_IDS = {
    "development": {
        "hardhat1:31337": 2,
        "hardhat2:31337": 2,
        "otp:2043": 2
    },
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

PRIVATE_HISTORICAL_REPOSITORY = "privateHistory"
PRIVATE_CURRENT_REPOSITORY = "privateCurrent"
