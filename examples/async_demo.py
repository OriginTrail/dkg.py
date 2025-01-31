import asyncio
import json
import time
from dkg import AsyncDKG
from dkg.constants import Environments, BlockchainIds
from dkg.providers import AsyncBlockchainProvider, AsyncNodeHTTPProvider


async def main():
    node_provider = AsyncNodeHTTPProvider(
        endpoint_uri="http://localhost:8900",
        api_version="v1",
    )

    # make sure that you have PRIVATE_KEY in .env so the blockchain provider can load it
    blockchain_provider = AsyncBlockchainProvider(
        Environments.DEVELOPMENT.value,
        BlockchainIds.HARDHAT_1.value,
    )

    dkg = AsyncDKG(
        node_provider,
        blockchain_provider,
        config={"max_number_of_retries": 300, "frequency": 2},
    )

    def divider():
        print("==================================================")
        print("==================================================")
        print("==================================================")

    def print_json(json_dict: dict):
        print(json.dumps(json_dict, indent=4))

    content = {
        "public": {
            "@context": "https://schema.org",
            "@id": "https://ford.mustang/2024",
            "@type": "Car",
            "name": "Ford Mustang",
            "brand": {"@type": "Brand", "name": "Ford"},
            "model": "Mustang",
            "manufacturer": {"@type": "Organization", "name": "Ford Motor Company"},
            "fuelType": "Gasoline",
            "numberOfDoors": 2,
            "vehicleEngine": {
                "@type": "EngineSpecification",
                "engineType": "V8",
                "enginePower": {
                    "@type": "QuantitativeValue",
                    "value": "450",
                    "unitCode": "BHP",
                },
            },
            "driveWheelConfiguration": "RWD",
            "speed": {"@type": "QuantitativeValue", "value": "240", "unitCode": "KMH"},
        }
    }

    divider()

    info_result = await dkg.node.info
    print("======================== NODE INFO RECEIVED")
    print_json(info_result)

    divider()

    start_time = time.perf_counter()
    create_asset_result = await dkg.asset.create(
        content=content,
        options={
            "epochs_num": 2,
            "minimum_number_of_finalization_confirmations": 3,
            "minimum_number_of_node_replications": 1,
        },
    )
    print(
        f"======================== ASSET CREATED in {time.perf_counter() - start_time} seconds"
    )
    print_json(create_asset_result)

    divider()

    start_time = time.perf_counter()
    get_result = await dkg.asset.get(create_asset_result.get("UAL"))
    print(
        f"======================== ASSET GET in {time.perf_counter() - start_time} seconds"
    )
    print_json(get_result)

    divider()

    start_time = time.perf_counter()
    transfer_result = await dkg.asset.transfer(
        create_asset_result.get("UAL"), "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    )
    print(
        f"======================== ASSET TRANSFER in {time.perf_counter() - start_time} seconds"
    )
    print_json(transfer_result)

    divider()

    # start_time = time.perf_counter()
    # # Burns knowledge collections
    # burn_result = await dkg.asset.burn(create_asset_result["UAL"], [1])
    # print(
    #     f"======================== ASSET BURN in {time.perf_counter() - start_time} seconds"
    # )
    # print_json(burn_result)

    # divider()

    start_time = time.perf_counter()
    query_operation_result = await dkg.graph.query(
        """
        PREFIX SCHEMA: <http://schema.org/>
        SELECT ?s ?modelName
        WHERE {
            ?s schema:model ?modelName .
        }
        """
    )
    print(
        f"======================== ASSET QUERY in {time.perf_counter() - start_time} seconds"
    )
    print_json(query_operation_result)

    divider()

    start_time = time.perf_counter()
    publish_finality_result = await dkg.graph.publish_finality(
        create_asset_result.get("UAL")
    )
    print(
        f"======================== PUBLISH FINALITY in {time.perf_counter() - start_time} seconds"
    )
    print_json(publish_finality_result)


if __name__ == "__main__":
    asyncio.run(main())
