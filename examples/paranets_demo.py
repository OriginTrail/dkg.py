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

import json

from hexbytes import HexBytes

from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.dataclasses import ParanetNodesAccessPolicy, ParanetMinersAccessPolicy

node_provider = NodeHTTPProvider("http://localhost:8900")
blockchain_provider = BlockchainProvider(
    "development",
    "hardhat2:31337",
    private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
)

dkg = DKG(node_provider, blockchain_provider)

def divider():
    print("==================================================")
    print("==================================================")
    print("==================================================")


def print_json(json_dict: dict):
    def convert_hexbytes(data):
        if isinstance(data, dict):
            return {k: convert_hexbytes(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_hexbytes(i) for i in data]
        elif isinstance(data, HexBytes):
            return data.to_0x_hex()
        else:
            return data

    serializable_dict = convert_hexbytes(json_dict)
    print(json.dumps(serializable_dict, indent=4))


divider()

paranet_data = {
    "public": {
        "@context": ["http://schema.org"],
        "@id": "uuid:1",
        "company": "OT",
        "city": {"@id": "uuid:belgrade"},
    }
}

create_paranet_knowledge_asset_result = dkg.asset.create(paranet_data, 1)

print("======================== PARANET KNOWLEDGE ASSET CREATED")
print_json(create_paranet_knowledge_asset_result)

divider()

paranet_ual = create_paranet_knowledge_asset_result["UAL"]
create_paranet_result = dkg.paranet.create(
    paranet_ual,
    "TestParanet",
    "TestParanetDescription",
    ParanetNodesAccessPolicy.OPEN,
    ParanetMinersAccessPolicy.OPEN
)

print("======================== PARANET CREATED")
print_json(create_paranet_result)

divider()

paranet_service_data = {
    "public": {
        "@context": ["http://schema.org"],
        "@id": "uuid:2",
        "service": "AI Agent Bob",
        "model": {"@id": "uuid:gpt4"},
    }
}

create_paranet_service_knowledge_asset_result = dkg.asset.create(
    paranet_service_data, 1
)

print("======================== PARANET SERVICE KNOWLEDGE ASSET CREATED")
print_json(create_paranet_service_knowledge_asset_result)

divider()

paranet_service_ual = create_paranet_service_knowledge_asset_result["UAL"]
create_paranet_service_result = dkg.paranet.create_service(
    paranet_service_ual,
    "TestParanetService",
    "TestParanetServiceDescription",
    ["0x03C094044301E082468876634F0b209E11d98452"],
)

print("======================== PARANET SERVICE CREATED")
print_json(create_paranet_service_result)

divider()

add_services_result = dkg.paranet.add_services(paranet_ual, [paranet_service_ual])

print("======================== ADDED PARANET SERVICES")
print_json(add_services_result)

divider()

incentives_pool_params = dkg.paranet.NeuroWebIncentivesPoolParams(
    neuro_emission_multiplier=1.1,
    operator_percentage=10.5,
    voters_percentage=5.5,
)
deploy_incentives_contract_result = dkg.paranet.deploy_incentives_contract(
    paranet_ual, incentives_pool_params
)

print("======================== PARANET NEURO INCENTIVES POOL DEPLOYED")
print_json(deploy_incentives_contract_result)

divider()

incentives_pool_address = dkg.paranet.get_incentives_pool_address(paranet_ual)

print("======================== GOT PARANET NEURO INCENTIVES POOL ADDRESS")
print(incentives_pool_address)

divider()

incentives_amount = blockchain_provider.w3.to_wei(100, "ether")
tx_hash = blockchain_provider.w3.eth.send_transaction(
    {
        "from": blockchain_provider.account.address,
        "to": incentives_pool_address,
        "value": incentives_amount,
    }
)

print(f"======================== SENT {incentives_amount} TO THE INCENTIVES POOL")

divider()

is_knowledge_miner = dkg.paranet.is_knowledge_miner(paranet_ual)
is_operator = dkg.paranet.is_operator(paranet_ual)
is_voter = dkg.paranet.is_voter(paranet_ual)

print(f"Is Knowledge Miner? {str(is_knowledge_miner)}")
print(f"Is Operator? {str(is_operator)}")
print(f"Is Voter? {str(is_voter)}")

divider()


def print_reward_stats(is_voter: bool = False):
    knowledge_miner_reward = dkg.paranet.calculate_claimable_miner_reward_amount(
        paranet_ual
    )
    operator_reward = dkg.paranet.calculate_claimable_operator_reward_amount(
        paranet_ual
    )

    print(
        f"Claimable Knowledge Miner Reward for the Current Wallet: {knowledge_miner_reward}"
    )
    print(
        f"Claimable Paranet Operator Reward for the Current Wallet: {operator_reward}"
    )
    if is_voter:
        voter_rewards = dkg.paranet.calculate_claimable_voter_reward_amount(paranet_ual)
        print(
            f"Claimable Proposal Voter Reward for the Current Wallet: {voter_rewards}"
        )

    divider()

    all_knowledge_miners_reward = (
        dkg.paranet.calculate_all_claimable_miner_rewards_amount(paranet_ual)
    )
    all_voters_reward = dkg.paranet.calculate_all_claimable_voters_reward_amount(
        paranet_ual
    )

    print(f"Claimable All Knowledge Miners Reward: {all_knowledge_miners_reward}")
    print(f"Claimable Paranet Operator Reward: {operator_reward}")
    print(f"Claimable All Proposal Voters Reward: {all_voters_reward}")


print_reward_stats(is_voter)

divider()

ka1 = {
    "public": {
        "@context": ["http://schema.org"],
        "@id": "uuid:3",
        "company": "KA1-Company",
        "user": {"@id": "uuid:user:1"},
        "city": {"@id": "uuid:belgrade"},
    }
}

create_submit_ka1_result = dkg.asset.create(
    ka1,
    1,
    100000000000000000000,
    paranet_ual=paranet_ual,
)

print(
    "======================== KNOWLEDGE ASSET #1 CREATED AND SUBMITTED TO THE PARANET"
)
print_json(create_submit_ka1_result)

divider()

ka2 = {
    "public": {
        "@context": ["http://schema.org"],
        "@id": "uuid:4",
        "company": "KA2-Company",
        "user": {"@id": "uuid:user:2"},
        "city": {"@id": "uuid:madrid"},
    }
}

create_ka2_result = dkg.asset.create(ka2, 1, 20000000000000000000)

print("======================== KNOWLEDGE ASSET #2 CREATED")
print_json(create_ka2_result)

ka2_ual = create_ka2_result["UAL"]
submit_ka2_result = dkg.asset.submit_to_paranet(ka2_ual, paranet_ual)

print("======================== KNOWLEDGE ASSET #2 SUBMITTED TO THE PARANET")
print_json(submit_ka2_result)

# divider()

# federated_query = """
# PREFIX schema: <http://schema.org/>
# SELECT DISTINCT ?s ?city1 ?user1 ?s2 ?city2 ?user2 ?company1
# WHERE {{
#     ?s schema:city ?city1 .
#     ?s schema:company ?company1 .
#     ?s schema:user ?user1;

#     SERVICE <{ual}> {{
#         ?s2 schema:city ?city2 .
#         ?s2 schema:user ?user2;
#     }}

#     filter(contains(str(?city2), "belgrade"))
# }}
# """
# query_result = dkg.graph.query(
#     federated_query.format(ual=ka2_ual),
#     paranet_ual,
# )

# print("======================== GOT FEDERATED QUERY RESULT")
# print(query_result)

divider()

is_knowledge_miner = dkg.paranet.is_knowledge_miner(paranet_ual)
is_operator = dkg.paranet.is_operator(paranet_ual)
is_voter = dkg.paranet.is_voter(paranet_ual)

print(f"Is Knowledge Miner? {str(is_knowledge_miner)}")
print(f"Is Operator? {str(is_operator)}")
print(f"Is Voter? {str(is_voter)}")

divider()

print_reward_stats(is_voter)

divider()

claim_miner_reward_result = dkg.paranet.claim_miner_reward(paranet_ual)

print("======================== KNOWLEDGE MINER REWARD CLAIMED")
print_json(claim_miner_reward_result)

divider()

claim_operator_reward_result = dkg.paranet.claim_operator_reward(paranet_ual)

print("======================== PARANET OPERATOR REWARD CLAIMED")
print(claim_operator_reward_result)

divider()

print_reward_stats()
