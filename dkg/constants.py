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

PRIVATE_ASSERTION_PREDICATE = (
    "https://ontology.origintrail.io/dkg/1.0#privateAssertionID"
)

BLOCKCHAINS = {
        2043: {
            "name": "otp",
            "hubAddress": "0x5fA7916c48Fe6D5F1738d12Ad234b78c90B4cAdA"
        },
        2160: {
            "name": "otp",
            "hubAddress": "0x833048F6e6BEa78E0AAdedeCd2Dc2231dda443FB"
        },
        20430: {
            "name": "otp",
            "hubAddress": "0xBbfF7Ea6b2Addc1f38A0798329e12C08f03750A6"
        },
        31337:  {
            "name": "hardhat",
            "hubAddress": "0x5FbDB2315678afecb367f032d93F642f64180aa3"
        },
    }

DEFAULT_HASH_FUNCTION_ID = 1
DEFAULT_SCORE_FUNCTION_ID = 1

PRIVATE_HISTORICAL_REPOSITORY = "privateHistory"
PRIVATE_CURRENT_REPOSITORY = "privateCurrent"
