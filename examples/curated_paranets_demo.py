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
import time

from hexbytes import HexBytes

from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.dataclasses import ParanetNodesAccessPolicy, ParanetMinersAccessPolicy

node_provider = NodeHTTPProvider("http://localhost:8900")
blockchain_provider = BlockchainProvider(
    "development",
    "hardhat2:31337",
    private_key="0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
)
blockchain_provider2 = BlockchainProvider(
    "development",
    "hardhat2:31337",
    private_key="0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
)
blockchain_provider3 = BlockchainProvider(
    "development",
    "hardhat2:31337",
    private_key="0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
)
blockchain_provider4 = BlockchainProvider(
    "development",
    "hardhat2:31337",
    private_key="0x9904da7fe786e5d1f8629b565b688425d78053d4325e746c5ad8ac4328248037",
)
blockchain_provider5 = BlockchainProvider(
    "development",
    "hardhat2:31337",
    private_key="0xfb07091daf99c1d493820ae8dcbc439b48b13ca844684bb1dcae27c9e680e62b",
)

dkg = DKG(node_provider, blockchain_provider)
dkg2 = DKG(node_provider, blockchain_provider2)
dkg3 = DKG(node_provider, blockchain_provider3)
dkg4 = DKG(node_provider, blockchain_provider4)
dkg5 = DKG(node_provider, blockchain_provider5)

node1_identity_id = dkg.node.get_identity_id(dkg.blockchain_provider.account.address)
node2_identity_id = dkg.node.get_identity_id(dkg2.blockchain_provider.account.address)
node3_identity_id = dkg.node.get_identity_id(dkg3.blockchain_provider.account.address)

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
    ParanetNodesAccessPolicy.CURATED,
    ParanetMinersAccessPolicy.CURATED
)

print("======================== A CURATED PARANET REGISTERED")
print_json(create_paranet_result)

divider()

identity_ids = [node1_identity_id, node2_identity_id, node3_identity_id]
dkg.paranet.add_curated_nodes(paranet_ual, identity_ids)
curated_nodes = dkg.paranet.get_curated_nodes(paranet_ual)
print("======================== ADDED NODES TO A CURATED PARANET")
print_json(curated_nodes)

divider()

identity_ids = [node2_identity_id, node3_identity_id]
dkg.paranet.remove_curated_nodes(paranet_ual, identity_ids)
curated_nodes = dkg.paranet.get_curated_nodes(paranet_ual)
print("======================== REMOVED NODES FROM A CURATED PARANET")
print_json({
    "paranetUAL": paranet_ual,
    "curatedNodes": curated_nodes
})

divider()

dkg2.paranet.request_curated_node_access(paranet_ual)
time.sleep(5)
dkg.paranet.reject_curated_node(paranet_ual, node2_identity_id)
print("======================== REJECT A NODE'S ACCESS REQUEST TO A CURATED PARANET")
curated_nodes = dkg.paranet.get_curated_nodes(paranet_ual)
print_json({
    "paranetUAL": paranet_ual,
    "curatedNodes": curated_nodes
})

divider()

dkg2.paranet.request_curated_node_access(paranet_ual)
time.sleep(5)
dkg.paranet.approve_curated_node(paranet_ual, node2_identity_id)
print("======================== APPROVE A NODE'S ACCESS REQUEST TO A CURATED PARANET")
curated_nodes = dkg.paranet.get_curated_nodes(paranet_ual)
print_json({
    "paranetUAL": paranet_ual,
    "curatedNodes": curated_nodes
})

divider()

miner_addresses = [
    dkg3.blockchain_provider.account.address,
    dkg4.blockchain_provider.account.address,
    dkg5.blockchain_provider.account.address,
]
dkg.paranet.add_curated_miners(paranet_ual, miner_addresses)
knowledge_miners = dkg.paranet.get_knowledge_miners(paranet_ual)
print("======================== ADDED KNOWLEDGE MINERS TO A CURATED PARANET")
print_json(knowledge_miners)

divider()

miner_addresses = [
    dkg4.blockchain_provider.account.address,
    dkg5.blockchain_provider.account.address,
]
dkg.paranet.remove_curated_miners(paranet_ual, miner_addresses)
knowledge_miners = dkg.paranet.get_knowledge_miners(paranet_ual)
print("======================== REMOVED KNOWLEDGE MINERS FROM A CURATED PARANET")
print_json({
    "paranetUAL": paranet_ual,
    "curatedNodes": knowledge_miners
})

divider()

dkg4.paranet.request_curated_miner_access(paranet_ual)
time.sleep(5)
dkg.paranet.reject_curated_miner(paranet_ual, dkg4.blockchain_provider.account.address)
print("======================== REJECT A MINER'S ACCESS REQUEST TO A CURATED PARANET")
knowledge_miners = dkg.paranet.get_knowledge_miners(paranet_ual)
print_json({
    "paranetUAL": paranet_ual,
    "curatedNodes": knowledge_miners
})

divider()

dkg4.paranet.request_curated_miner_access(paranet_ual)
time.sleep(5)
dkg.paranet.approve_curated_miner(paranet_ual, dkg4.blockchain_provider.account.address)
print("======================== APPROVE A MINER'S ACCESS REQUEST TO A CURATED PARANET")
knowledge_miners = dkg.paranet.get_knowledge_miners(paranet_ual)
print_json({
    "paranetUAL": paranet_ual,
    "curatedNodes": knowledge_miners
})

divider()

create_first_asset_result = dkg3.asset.create(paranet_data, 1)
approved_submit_result = dkg3.asset.submit_to_paranet(
    create_first_asset_result.get("UAL"),
    paranet_ual,
)
print(
    "======================== CREATE A KA AND SUBMIT IT TO A CURATED PARANET - "
    "KNOWLEDGE MINER IS APPROVED"
)
print_json({
    "paranetUAL": paranet_ual,
    "assetUAL": create_first_asset_result.get("UAL"),
    "submitResult": approved_submit_result
})

divider()

create_second_asset_result = dkg5.asset.create(paranet_data, 1)
not_approved_submit_result = None
try:
    not_approved_submit_result = dkg5.asset.submit_to_paranet(
        create_second_asset_result.get("UAL"),
        paranet_ual,
    )
except Exception as e:
    not_approved_submit_result = e.args[0]
print(
    "======================== CREATE A KA AND SUBMIT IT TO A CURATED PARANET - "
    "KNOWLEDGE MINER IS NOT APPROVED"
)
print_json({
    "paranetUAL": paranet_ual,
    "assetUAL": create_second_asset_result.get("UAL"),
    "submitResult": not_approved_submit_result
})

divider()