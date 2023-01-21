from .encoding import DataHexStr
from typing import NewType

Address = NewType("Address", DataHexStr)
