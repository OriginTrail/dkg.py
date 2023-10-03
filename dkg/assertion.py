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

from dkg.manager import DefaultRequestManager
from dkg.module import Module
from dkg.types import JSONLD, HexStr
from dkg.utils.merkle import MerkleTree, hash_assertion_with_indexes
from dkg.utils.metadata import generate_assertion_metadata
from dkg.utils.rdf import format_content


class Assertion(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    def format_graph(self, content: dict[Literal["public", "private"], JSONLD]):
        return format_content(content)

    def get_public_assertion_id(
        self, content: dict[Literal["public", "private"], JSONLD]
    ) -> HexStr:
        assertions = format_content(content)

        return MerkleTree(
            hash_assertion_with_indexes(assertions["public"]),
            sort_pairs=True,
        ).root

    def get_size(self, content: dict[Literal["public", "private"], JSONLD]) -> int:
        assertions = format_content(content)
        public_assertion_metadata = generate_assertion_metadata(assertions["public"])

        return public_assertion_metadata["size"]

    def get_triples_number(
        self, content: dict[Literal["public", "private"], JSONLD]
    ) -> int:
        assertions = format_content(content)
        public_assertion_metadata = generate_assertion_metadata(assertions["public"])

        return public_assertion_metadata["triples_number"]

    def get_chunks_number(
        self, content: dict[Literal["public", "private"], JSONLD]
    ) -> int:
        assertions = format_content(content)
        public_assertion_metadata = generate_assertion_metadata(assertions["public"])

        return public_assertion_metadata["chunks_number"]
