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

import asyncio
import json
from dkg import AsyncDKG
from dkg.constants import Environments, BlockchainIds
from dkg.providers import AsyncBlockchainProvider, AsyncNodeHTTPProvider
from dkg.dataclasses import (
    ParanetNodesAccessPolicy,
    ParanetMinersAccessPolicy,
)


async def main():
    node_provider = AsyncNodeHTTPProvider(endpoint_uri="http://localhost:8900")

    # IMPORTANT: make sure that you have PRIVATE_KEY in .env so the blockchain provider can load it
    blockchain_provider = AsyncBlockchainProvider(
        Environments.DEVELOPMENT.value,
        BlockchainIds.HARDHAT_1.value,
    )

    # here you can create your own custom values that will be applied to all the functions
    config = {
        "max_number_of_retries": 300,
        "frequency": 2,
    }
    dkg = AsyncDKG(node_provider, blockchain_provider, config)

    def divider():
        print("==================================================")
        print("==================================================")
        print("==================================================")

    def print_json(json_dict: dict):
        print(json.dumps(json_dict, indent=4))

    divider()

    info_result = await dkg.node.info

    print("======================== NODE INFO RECEIVED")
    print_json(info_result)

    paranet_content = {
        "public": {
            "@context": "https://www.schema.org",
            "@id": "urn:us-cities:info:new-york",
            "@type": "City",
            "name": "New York",
            "state": "New York",
            "population": "8,336,817",
            "area": "468.9 sq mi",
        },
        "private": {
            "@context": "https://www.schema.org",
            "@id": "urn:us-cities:data:new-york",
            "@type": "CityPrivateData",
            "crimeRate": "Low",
            "averageIncome": "$63,998",
            "infrastructureScore": "8.5",
            "relatedCities": [
                {"@id": "urn:us-cities:info:los-angeles", "name": "Los Angeles"},
                {"@id": "urn:us-cities:info:chicago", "name": "Chicago"},
            ],
        },
    }

    create_paranet_knowledge_collection_result = await dkg.asset.create(
        content=paranet_content, options={"epochs_num": 2}
    )

    print("======================== PARANET KNOWLEDGE COLLECTION CREATED")
    print_json(create_paranet_knowledge_collection_result)

    divider()

    # Paranet UAL is a Knowledge Asset UAL (combination of Knowledge Collection UAL and Knowledge Asset token id)
    paranet_ual = f"{create_paranet_knowledge_collection_result['UAL']}/1"
    paranet_options = {
        "paranet_name": "FirstParanet",
        "paranet_description": "First ever paranet on DKG!",
        "trac_to_neuro_emission_multiplier": 5,
        "incentivization_proposal_voters_reward_percentage": 12.0,
        "operator_reward_percentage": 10.0,
        "paranet_nodes_access_policy": ParanetNodesAccessPolicy.OPEN,
        "paranet_miners_access_policy": ParanetMinersAccessPolicy.OPEN,
    }

    create_paranet_result = await dkg.paranet.create(paranet_ual, paranet_options)

    print("======================== PARANET REGISTERED")
    print_json(create_paranet_result)

    divider()

    incentives_pool_params = dkg.paranet.NeuroWebIncentivesPoolParams(
        neuro_emission_multiplier=1.1, operator_percentage=10.5, voters_percentage=5.5
    )
    deploy_incentives_contract_result = await dkg.paranet.deploy_incentives_contract(
        paranet_ual, incentives_pool_params
    )

    print("======================== PARANET NEURO INCENTIVES POOL DEPLOYED")
    print_json(deploy_incentives_contract_result)

    divider()

    incentives_pool_address = await dkg.paranet.get_incentives_pool_address(paranet_ual)

    print("======================== GOT PARANET NEURO INCENTIVES POOL ADDRESS")
    print(incentives_pool_address)

    divider()

    incentives_amount = blockchain_provider.w3.to_wei(100, "ether")
    await blockchain_provider.w3.eth.send_transaction(
        {
            "from": blockchain_provider.account.address,
            "to": incentives_pool_address,
            "value": incentives_amount,
        }
    )

    print(f"======================== SENT {incentives_amount} TO THE INCENTIVES POOL")

    divider()

    service_content = {
        "public": {
            "@context": "https://www.schema.org",
            "@id": "urn:us-cities:info:miami",
            "@type": "City",
            "name": "Miami",
            "state": "Florida",
            "population": "2,000,000",
            "area": "135.2 sq mi",
        },
        "private": {
            "@context": "https://www.schema.org",
            "@id": "urn:us-cities:data:miami",
            "@type": "CityPrivateData",
            "crimeRate": "Low",
            "averageIncome": "$100,998",
            "infrastructureScore": "7.5",
            "relatedCities": [
                {"@id": "urn:us-cities:info:austin", "name": "Austin"},
                {"@id": "urn:us-cities:info:seattle", "name": "Seattle"},
            ],
        },
    }

    create_paranet_service_kc_result = await dkg.asset.create(
        content=service_content,
        options={"epochs_num": 2},
    )

    print("======================== PARANET SERVICE KNOWLEDGE COLLECTION CREATED")
    print_json(create_paranet_service_kc_result)

    divider()
    # Paranet service UAL is a Knowledge Asset UAL (combination of Knowledge Collection UAL and Knowledge Asset token id)
    paranet_service_ual = f"{create_paranet_service_kc_result['UAL']}/1"

    submit_to_paranet = await dkg.asset.submit_to_paranet(
        paranet_service_ual, paranet_ual
    )

    print("======================== SUBMITED TO PARANET")
    print_json(submit_to_paranet)

    divider()

    create_paranet_service_result = await dkg.paranet.create_service(
        ual=paranet_service_ual,
        options={
            "paranet_service_name": "FKPS",
            "paranet_service_description": "Fast Knowledge Processing Service",
            "paranet_service_addresses": [],
        },
    )

    print("======================== PARANET SERVICE CREATED")
    print_json(create_paranet_service_result)

    divider()

    add_services_result = await dkg.paranet.add_services(
        paranet_ual, [paranet_service_ual]
    )

    print("======================== ADDED PARANET SERVICES")
    print_json(add_services_result)

    divider()

    is_knowledge_miner = await dkg.paranet.is_knowledge_miner(paranet_ual)
    print(f"Is Knowledge Miner? {str(is_knowledge_miner)}")

    is_operator = await dkg.paranet.is_operator(paranet_ual)
    print(f"Is Operator? {str(is_operator)}")

    is_voter = await dkg.paranet.is_voter(paranet_ual)
    print(f"Is Voter? {str(is_voter)}")

    divider()

    # def print_reward_stats(is_voter: bool = False):
    #     knowledge_miner_reward = dkg.paranet.calculate_claimable_miner_reward_amount(
    #         paranet_ual
    #     )
    #     operator_reward = dkg.paranet.calculate_claimable_operator_reward_amount(
    #         paranet_ual
    #     )

    #     print(
    #         f"Claimable Knowledge Miner Reward for the Current Wallet: {knowledge_miner_reward}"
    #     )
    #     print(
    #         f"Claimable Paranet Operator Reward for the Current Wallet: {operator_reward}"
    #     )
    #     if is_voter:
    #         voter_rewards = dkg.paranet.calculate_claimable_voter_reward_amount(paranet_ual)
    #         print(
    #             f"Claimable Proposal Voter Reward for the Current Wallet: {voter_rewards}"
    #         )

    #     divider()

    #     all_knowledge_miners_reward = (
    #         dkg.paranet.calculate_all_claimable_miner_rewards_amount(paranet_ual)
    #     )
    #     all_voters_reward = dkg.paranet.calculate_all_claimable_voters_reward_amount(
    #         paranet_ual
    #     )

    #     print(f"Claimable All Knowledge Miners Reward: {all_knowledge_miners_reward}")
    #     print(f"Claimable Paranet Operator Reward: {operator_reward}")
    #     print(f"Claimable All Proposal Voters Reward: {all_voters_reward}")

    # print_reward_stats(is_voter)

    # divider()

    # claim_miner_reward_result = dkg.paranet.claim_miner_reward(paranet_ual)

    # print("======================== KNOWLEDGE MINER REWARD CLAIMED")
    # print_json(claim_miner_reward_result)

    # divider()

    # claim_operator_reward_result = dkg.paranet.claim_operator_reward(paranet_ual)

    # print("======================== PARANET OPERATOR REWARD CLAIMED")
    # print(claim_operator_reward_result)

    # divider()

    # print_reward_stats()

    # divider()

    denver_content = {
        "public": {
            "@context": "https://www.schema.org",
            "@id": "urn:us-cities:info:denver",
            "@type": "City",
            "name": "Denver",
            "state": "Colorado",
            "population": "700,000",
            "area": "153.3 sq mi",
        },
        "private": {
            "@context": "https://www.schema.org",
            "@id": "urn:us-cities:data:denver",
            "@type": "CityPrivateData",
            "crimeRate": "Low",
            "averageIncome": "$50,998",
            "infrastructureScore": "6.5",
            "relatedCities": [
                {"@id": "urn:us-cities:info:boston", "name": "Boston"},
                {"@id": "urn:us-cities:info:chicago", "name": "Chicago"},
            ],
        },
    }

    create_collection_result = await dkg.asset.create(
        content=denver_content, options={"epochs_num": 2}
    )

    print("======================== KNOWLEDGE COLLECTION #1 CREATED")
    print_json(create_collection_result)

    divider()

    submit_to_paranet_result = await dkg.asset.submit_to_paranet(
        create_collection_result["UAL"], paranet_ual
    )

    print("======================== KNOWLEDGE COLLECTION #1 SUBMITED TO THE PARANET")
    print_json(submit_to_paranet_result)

    divider()

    dallas_content = {
        "public": {
            "@context": "https://www.schema.org",
            "@id": "urn:us-cities:info:dallas",
            "@type": "City",
            "name": "Dallas",
            "state": "Texas",
            "population": "1,343,573",
            "area": "386.5 sq mi",
        },
        "private": {
            "@context": "https://www.schema.org",
            "@id": "urn:us-cities:data:dallas",
            "@type": "CityPrivateData",
            "crimeRate": "Low",
            "averageIncome": "$80,998",
            "infrastructureScore": "7.5",
            "relatedCities": [
                {"@id": "urn:us-cities:info:austin", "name": "Austin"},
                {"@id": "urn:us-cities:info:houston", "name": "Houston"},
            ],
        },
    }

    create_collection_result2 = await dkg.asset.create(
        content=dallas_content, options={"epochs_num": 2}
    )
    print("======================== KNOWLEDGE COLLECTION #2 CREATED")
    print_json(create_collection_result2)

    submit_to_paranet_result2 = await dkg.asset.submit_to_paranet(
        create_collection_result2["UAL"], paranet_ual
    )

    print("======================== KNOWLEDGE COLLECTION #2 SUBMITTED TO THE PARANET")
    print_json(submit_to_paranet_result2)

    divider()

    # IMPORTANT: For queries to work, you need to add assetSync to your node's .origintrail_noderc file.
    # How to: https://docs.origintrail.io/dkg-v6-previous-version/node-setup-instructions/sync-a-dkg-paranet
    query_where_denver = """
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT ?graphName
    WHERE {
        GRAPH ?graphName {
        ?s schema:name "Denver" .
        }
    }
    """
    query_result = await dkg.graph.query(
        query=query_where_denver, options={"paranet_ual": paranet_ual}
    )

    print("======================== QUERY PARANET REPOSITORY RESULT")
    print_json(query_result)

    divider()

    federated_query = f"""
    PREFIX schema: <http://schema.org/>
    SELECT DISTINCT ?s ?state1 ?name1 ?s2 ?state2 ?name2 ?population1
    WHERE {{
        ?s schema:state ?state1 .
        ?s schema:name ?name1 .
        ?s schema:population ?population1 .

        SERVICE <{paranet_ual}> {{
            ?s2 schema:state "Colorado" .
            ?s2 schema:name "Denver" .
            ?s2 schema:state ?state2 .
            ?s2 schema:name ?name2 .
        }}

        filter(contains(str(?name2), "Denver"))
    }}
    """
    query_result = await dkg.graph.query(
        query=federated_query, options={"paranet_ual": paranet_ual}
    )

    print("======================== FEDERATED QUERY RESULT")
    print_json(query_result)

    divider()


if __name__ == "__main__":
    asyncio.run(main())
