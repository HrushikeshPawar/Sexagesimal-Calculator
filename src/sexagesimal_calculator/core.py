from dataclasses import dataclass
from typing import Tuple

# Constants
BASE = 60
PART_SEP = ";"
VAL_SEP = ","


@dataclass(frozen=True, slots=True)
class SexagesimalParts:
    """
    An immutable, private container for the normalized components of a
    sexagesimal number.

    Using frozen=True makes instances immutable and hashable.
    Using slots=True optimizes memory usage and attribute access speed.
    """

    is_negative: bool
    integer_part: Tuple[int, ...]
    fractional_part: Tuple[int, ...]
