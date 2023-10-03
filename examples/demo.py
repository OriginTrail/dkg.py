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

import math
import random
import time

from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider

node_provider = NodeHTTPProvider("http://localhost:8900")
blockchain_provider = BlockchainProvider(
    "http://localhost:8545",
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
)

dkg = DKG(node_provider, blockchain_provider)


def divider():
    print("==================================================")
    print("==================================================")
    print("==================================================")


content = {
    "public": {
        "@context": ["http://schema.org"],
        "@id": "uuid:1",
        "company": "OT",
        "user": {"@id": "uuid:user:1"},
        "city": {"@id": "uuid:belgrade"},
    },
    "private": {
        "@context": ["http://schema.org"],
        "@graph": [
            {"@id": "uuid:user:1", "name": "Adam", "lastname": "Smith"},
            {"@id": "uuid:belgrade", "title": "Belgrade", "postCode": "11000"},
        ],
    },
}


divider()

info_result = dkg.node.info

print("======================== NODE INFO RECEIVED")
print(info_result)

divider()

formatted_assertions = dkg.assertion.format_graph(content)
print("======================== ASSET FORMATTED")
print(formatted_assertions)

divider()

public_assertion_id = dkg.assertion.get_public_assertion_id(content)
print("======================== PUBLIC ASSERTION ID (MERKLE ROOT) CALCULATED")
print(public_assertion_id)

divider()

public_assertion_size = dkg.assertion.get_size(content)
print("======================== PUBLIC ASSERTION SIZE CALCULATED")
print(public_assertion_size)

divider()

public_assertion_triples_number = dkg.assertion.get_triples_number(content)
print("======================== PUBLIC ASSERTION TRIPLES NUMBER CALCULATED")
print(public_assertion_triples_number)

divider()

public_assertion_chunks_number = dkg.assertion.get_chunks_number(content)
print("======================== PUBLIC ASSERTION CHUNKS NUMBER CALCULATED")
print(public_assertion_chunks_number)

divider()

bid_suggestion = dkg.network.get_bid_suggestion(
    public_assertion_id,
    public_assertion_size,
    2,
)
print("======================== BID SUGGESTION CALCULATED")
print(bid_suggestion)

divider()

current_allowance = dkg.asset.get_current_allowance()
print("======================== GET CURRENT ALLOWANCE")
print(current_allowance)

divider()

allowance_increase = dkg.asset.increase_allowance(bid_suggestion)
print("======================== INCREASE ALLOWANCE")
print(allowance_increase)

divider()

allowance_decrease = dkg.asset.decrease_allowance(bid_suggestion // 3)
print("======================== DECREASE ALLOWANCE")
print(allowance_decrease)

divider()

allowance_set = dkg.asset.set_allowance(bid_suggestion)
print("======================== SET ALLOWANCE")
print(allowance_set)

divider()

create_asset_result = dkg.asset.create(content, 2)
print("======================== ASSET CREATED")
print(create_asset_result)
divider()

owner_result = dkg.asset.get_owner(create_asset_result["UAL"])
print("======================== GET ASSET OWNER")
print(owner_result)
divider()

get_asset_result = dkg.asset.get(create_asset_result["UAL"])
print("======================== ASSET RESOLVED")
print(get_asset_result)
divider()

update_asset_result = dkg.asset.update(
    create_asset_result["UAL"],
    {
        "private": {
            "@context": ["https://schema.org"],
            "@graph": [
                {
                    "@id": "uuid:user:1",
                    "name": "Adam",
                    "lastname": "Smith",
                    "identifier": f"{math.floor(random.random() * 1e10)}",
                },
            ],
        },
    },
)
print("======================== ASSET UPDATED")
print(update_asset_result)
divider()

get_latest_asset_result = dkg.asset.get(
    create_asset_result["UAL"], "latest", "all"
)
print("======================== ASSET LATEST RESOLVED")
print(get_latest_asset_result)
divider()

get_latest_finalized_asset_result = dkg.asset.get(
    create_asset_result["UAL"], "latest_finalized", "all"
)
print("======================== ASSET LATEST FINALIZED RESOLVED")
print(get_latest_finalized_asset_result)
divider()

get_first_state_by_index = dkg.asset.get(create_asset_result["UAL"], 0, "all")
print("======================== ASSET FIRST STATE (GET BY STATE INDEX) RESOLVED")
print(get_first_state_by_index)
divider()

# TODO: Remove when wait_for_finalization is implemented
time.sleep(30)

get_second_state_by_index = dkg.asset.get(create_asset_result["UAL"], 1, "all")
print("======================== ASSET SECOND STATE (GET BY STATE INDEX) RESOLVED")
print(get_second_state_by_index)
divider()

get_first_state_by_hash = dkg.asset.get(
    create_asset_result["UAL"], create_asset_result["publicAssertionId"], "all"
)
print("======================== ASSET FIRST STATE (GET BY STATE HASH) RESOLVED")
print(get_first_state_by_hash)
divider()

get_second_state_by_hash = dkg.asset.get(
    create_asset_result["UAL"], update_asset_result["publicAssertionId"], "all"
)
print("======================== ASSET SECOND STATE (GET BY STATE HASH) RESOLVED")
print(get_second_state_by_hash)
divider()

query_result = dkg.graph.query(
    "construct { ?s ?p ?o } where { ?s ?p ?o . <uuid:user:1> ?p ?o }", "privateCurrent"
)
print("======================== QUERY LOCAL CURRENT RESULT")
print(query_result)
