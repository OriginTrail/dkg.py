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

from dkg.exceptions import DatasetInputFormatNotSupported, InvalidDataset
from dkg.types import JSONLD, NQuads
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
