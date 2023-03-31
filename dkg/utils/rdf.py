from typing import Literal

from dkg.exceptions import DatasetInputFormatNotSupported, InvalidDataset
from dkg.types import JSONLD, NQuads
from pyld import jsonld


def normalize_dataset(
    dataset: JSONLD | NQuads,
    input_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
) -> NQuads:
    """
    Normalizes a dataset provided in JSON-LD or N-Quads format using the URDNA2015 algorithm.

    Args:
        dataset (JSONLD | NQuads): The dataset to be normalized, in either JSON-LD or N-Quads
        format.
        input_format (Literal['JSON-LD', 'N-Quads'], optional): The format of the input dataset.
        Defaults to 'JSON-LD'.

    Returns:
        NQuads: The normalized dataset in N-Quads format.

    Raises:
        DatasetInputFormatNotSupported: If the input_format is not supported.
        InvalidDataset: If the input dataset is not valid and no quads were extracted.

    Example:

        dataset = {
            "@context": {...},
            "@id": "http://example.org/test",
            "http://example.org/name": [{"@value": "example name"}]
        }
        normalize_dataset(dataset, input_format='JSON-LD')
    """
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
