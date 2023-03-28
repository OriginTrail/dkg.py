from dkg.types import JSONLD, NQuads
from typing import Literal
from pyld import jsonld
from dkg.exceptions import DatasetInputFormatNotSupported, InvalidDataset


def normalize_dataset(
    dataset: JSONLD | NQuads,
    input_format: Literal['JSON-LD', 'N-Quads'] = 'JSON-LD',
) -> NQuads:
    normalization_options = {
        'algorithm': 'URDNA2015',
        'format': 'application/n-quads',
    }

    match input_format.lower():
        case 'json-ld' | 'jsonld':
            pass
        case 'n-quads' | 'nquads':
            normalization_options['inputFormat'] = 'application/n-quads'
        case _:
            raise DatasetInputFormatNotSupported(
                f'Dataset input format isn\'t supported: {input_format}. '
                'Supported formats: JSON-LD / N-Quads.'
            )

    n_quads = jsonld.normalize(dataset, normalization_options)
    assertion = [quad for quad in n_quads.split('\n') if quad]

    if not assertion:
        raise InvalidDataset('Invalid dataset, no quads were extracted.')

    return assertion
