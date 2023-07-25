import math
import random
from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.dataclasses import (KnowledgeAssetEnumStates)

node_provider = NodeHTTPProvider(
    'http://localhost:8900'
    )
blockchain_provider = BlockchainProvider(
    'http://localhost:8545', 
    '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
    )

dkg = DKG(node_provider, blockchain_provider)

def divider():
    print('==================================================')
    print('==================================================')
    print('==================================================')

divider()

infoResult: any = dkg.node.info

print('======================== NODE INFO RECEIVED')
print(infoResult)

divider()

createAssetResult: any = dkg.asset.create({
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
    }, 2)
print('======================== ASSET CREATED')
print(createAssetResult)
divider()

ownerResult: any = dkg.asset.getOwner(createAssetResult['UAL'])
print('======================== GET ASSET OWNER')
print(ownerResult)
divider()

getAssetResult: any = dkg.asset.get(createAssetResult['UAL'])
print('======================== ASSET RESOLVED')
print(ownerResult)
divider()

updateAssetResult: any = dkg.asset.update(createAssetResult['UAL'], {
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
    })
print('======================== ASSET UPDATED')
print(updateAssetResult)
divider()

getLatestFinalizedAssetResult: any = dkg.asset.get(createAssetResult['UAL'], "latest_finalized", "all")
print('======================== ASSET LATEST FINALIZED RESOLVED')
print(getLatestFinalizedAssetResult)
divider()

getLatestFinalizedAssetResult: any = dkg.asset.get(createAssetResult['UAL'], "latest_finalized", "all")
print('======================== ASSET LATEST FINALIZED RESOLVED')
print(getLatestFinalizedAssetResult)
divider()

getFirstStateByIndex: any = dkg.asset.get(createAssetResult['UAL'], 0, "all")
print('======================== ASSET FIRST STATE (GET BY STATE INDEX) RESOLVED')
print(getFirstStateByIndex)
divider()

getSecondStateByIndex: any = dkg.asset.get(createAssetResult['UAL'], 1, "all")
print('======================== ASSET SECOND STATE (GET BY STATE INDEX) RESOLVED')
print(getSecondStateByIndex)
divider()

getFirstStateByHash: any = dkg.asset.get(createAssetResult['UAL'], createAssetResult['publicAssertionId'], "all")
print('======================== ASSET FIRST STATE (GET BY STATE HASH) RESOLVED')
print(getFirstStateByHash)
divider()

getSecondStateByHash: any = dkg.asset.get(createAssetResult['UAL'], updateAssetResult['publicAssertionId'], "all")
print('======================== ASSET SECOND STATE (GET BY STATE HASH) RESOLVED')
print(getSecondStateByHash)
divider()

queryResult = dkg.graph.query('construct { ?s ?p ?o } where { ?s ?p ?o . <uuid:1> ?p ?o }', 'privateCurrent')
print('======================== QUERY LOCAL CURRENT RESULT')
print(queryResult)
divider()
