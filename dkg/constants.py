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
        "otp:2043": {
            "hub": "0x7585a99C5C150a08f5CDeFD16465C6De8D41EbbD",
            "rpc": "http://parachain-alphanet-02.origin-trail.network:9933",
        },
    },
    "devnet": {
        "otp:2160": {
            "hub": "0x833048F6e6BEa78E0AAdedeCd2Dc2231dda443FB",
            "rpc": "https://lofar-tm-rpc.origin-trail.network",
        },
        "gnosis:10200": {
            "hub": "0xD2bA102A0b11944d00180eE8136208ccF87bC39A",
            "rpc": "https://rpc.chiadochain.net",
            "gas_price_oracle": "https://blockscout.chiadochain.net/api/v1/gas-price-oracle",
        },
    },
    "testnet": {
        "otp:20430": {
            "hub": "0xBbfF7Ea6b2Addc1f38A0798329e12C08f03750A6",
            "rpc": "https://lofar-testnet.origin-trail.network",
        },
        "gnosis:10200": {
            "hub": "0xC06210312C9217A0EdF67453618F5eB96668679A",
            "rpc": "https://rpc.chiadochain.net",
            "gas_price_oracle": "https://blockscout.chiadochain.net/api/v1/gas-price-oracle",
        },
    },
    "mainnet": {
        "otp:2043": {
            "hub": "0x5fA7916c48Fe6D5F1738d12Ad234b78c90B4cAdA",
            "rpc": "https://astrosat-parachain-rpc.origin-trail.network",
        },
    },
}

DEFAULT_GAS_PRICE_GWEI = 100

DEFAULT_HASH_FUNCTION_ID = 1
DEFAULT_SCORE_FUNCTION_ID = 1

PRIVATE_HISTORICAL_REPOSITORY = "privateHistory"
PRIVATE_CURRENT_REPOSITORY = "privateCurrent"
