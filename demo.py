import json
from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.dataclasses import (KnowledgeAssetEnumStates)

node_provider = NodeHTTPProvider('http://localhost:8900')
blockchain_provider = BlockchainProvider('http://localhost:8545', '0x5FbDB2315678afecb367f032d93F642f64180aa3', '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80')

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

createAssetResult: any = dkg.asset.create(json.loads("""
    {
        "public": {
            "@context": [
                "https://schema.org"
            ],
            "@id": "uuid:1",
            "company": "OT",
            "user": {
                "@id": "uuid:user:1"
            },
            "city": {
                "@id": "uuid:belgrade"
            }
        },
        "private": {
            "@context": [
                "https://schema.org"
            ],
            "@graph": [
                {
                    "@id": "uuid:user:1",
                    "name": "Adam",
                    "lastname": "Smith"
                },
                {
                    "@id": "uuid:belgrade",
                    "title": "Belgrade",
                    "postCode": "11000"
                }
            ]
        }
    }"""), 2)
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

updateAssetResult: any = dkg.asset.update(createAssetResult['UAL'], json.loads("""
{
    "public": {
        "@context": [
            "https://schema.org"
        ],
        "@id": "uuid:1",
        "company": "TL",
        "user": {
            "@id": "uuid:user:2"
        },
        "city": {
            "@id": "uuid:Nis"
        }
    },
    "private": {
        "@context": [
            "https://schema.org"
        ],
        "@graph": [
            {
                "@id": "uuid:user:1",
                "name": "Adam",
                "lastname": "Smith",
                "identifier": "9496699517"
            }
        ]
    }
}
"""))
print('======================== ASSET UPDATED')
print(updateAssetResult)
divider()

getLatestFinalizedAssetResult: any = dkg.asset.get(createAssetResult['UAL'], KnowledgeAssetEnumStates.LATEST_FINALIZED)
print('======================== ASSET LATEST FINALIZED RESOLVED')
print(getLatestFinalizedAssetResult)
divider()


# todo implement wait finalization method

# dkg.asset.waitFinalization(createAssetResult['UAL'])
# print('======================== FINALIZATION COMPLETED')
# divider()

getLatestFinalizedAssetResult: any = dkg.asset.get(createAssetResult['UAL'], KnowledgeAssetEnumStates.LATEST_FINALIZED)
print('======================== ASSET LATEST FINALIZED RESOLVED')
print(getLatestFinalizedAssetResult)
divider()

getFirstStateByIndex: any = dkg.asset.get(createAssetResult['UAL'], 0)
print('======================== ASSET FIRST STATE (GET BY STATE INDEX) RESOLVED')
print(getFirstStateByIndex)
divider()

getSecondStateByIndex: any = dkg.asset.get(createAssetResult['UAL'], 1)
print('======================== ASSET SECOND STATE (GET BY STATE INDEX) RESOLVED')
print(getSecondStateByIndex)
divider()

getFirstStateByHash: any = dkg.asset.get(createAssetResult['UAL'], createAssetResult['publicAssertionId'])
print('======================== ASSET FIRST STATE (GET BY STATE HASH) RESOLVED')
print(getFirstStateByHash)
divider()

getSecondStateByHash: any = dkg.asset.get(createAssetResult['UAL'], updateAssetResult['publicAssertionId'])
print('======================== ASSET SECOND STATE (GET BY STATE HASH) RESOLVED')
print(getSecondStateByHash)
divider()

queryResult = dkg.graph.query('construct { ?s ?p ?o } where { ?s ?p ?o . <uuid:1> ?p ?o }', 'PUBLIC_CURRENT')
print('======================== QUERY LOCAL CURRENT RESULT')
print(queryResult)
divider()

new_owner = '0x2ACa90078563133db78085F66e6B8Cf5531623Ad'
transferResult = dkg.asset.transfer(createAssetResult.UAL, new_owner)
print('======================== ASSET TRANSFERRED')
print(transferResult)
divider()