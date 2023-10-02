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

from typing import Literal

from dkg.constants import PRIVATE_ASSERTION_PREDICATE
from dkg.exceptions import DatasetInputFormatNotSupported, InvalidDataset
from dkg.types import JSONLD, HexStr, NQuads
from dkg.utils.merkle import MerkleTree, hash_assertion_with_indexes
from pyld import jsonld


def normalize_dataset(
    dataset: JSONLD | NQuads,
    input_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
) -> NQuads:
    normalization_options = {
        "algorithm": "URDNA2015",
        "format": "application/n-quads",
    }

    match input_format.lower():
        case "json-ld" | "jsonld":
            pass
        case "n-quads" | "nquads":
            normalization_options["inputFormat"] = "application/n-quads"
        case _:
            raise DatasetInputFormatNotSupported(
                f"Dataset input format isn't supported: {input_format}. "
                "Supported formats: JSON-LD / N-Quads."
            )

    n_quads = jsonld.normalize(dataset, normalization_options)
    assertion = [quad for quad in n_quads.split("\n") if quad]

    if not assertion:
        raise InvalidDataset("Invalid dataset, no quads were extracted.")

    return assertion


def format_content(
    content: dict[Literal["public", "private"], JSONLD],
    type: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
) -> dict[str, dict[str, HexStr | NQuads | int]]:
    public_graph = {"@graph": []}

    if content.get("public", None):
        public_graph["@graph"].append(content["public"])

    if content.get("private", None):
        private_assertion = normalize_dataset(content["private"], type)
        private_assertion_id = MerkleTree(
            hash_assertion_with_indexes(private_assertion),
            sort_pairs=True,
        ).root

        public_graph["@graph"].append(
            {PRIVATE_ASSERTION_PREDICATE: private_assertion_id}
        )

    public_assertion = normalize_dataset(public_graph, type)

    return {
        "public": public_assertion,
        "private": private_assertion
        if content.get("private", None)
        else {},
    }
