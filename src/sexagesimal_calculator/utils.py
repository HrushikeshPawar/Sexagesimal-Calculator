from typing import List

from sexagesimal_calculator.core import _SexagesimalParts


def _normalize_parts(integer_parts: List[int], fractional_parts: List[int], is_negative: bool) -> _SexagesimalParts:
    """
    Normalize integer and fractional sexagesimal digit lists into a canonical parts container.

    Summary:
        Cleans up the provided integer and fractional digit lists so they represent a
        canonical, immutable sexagesimal value. This includes:
            - removing extraneous leading zeros from the integer part,
            - removing extraneous trailing zeros from the fractional part,
            - ensuring a canonical representation for zero (integer_part=(0,), fractional_part=(0,)),
            - preserving the sign except that zero is always non-negative.

    Notes:
        - The function returns a frozen _SexagesimalParts dataclass suitable for storage
            on Sexagesimal instances.
        - The implementation operates in-place on the provided lists (it mutates the
            lists by popping). Callers who need to keep their originals should pass copies.
        - The canonical fractional part is always non-empty; if all fractional digits are
            stripped, it becomes [0].

    Args:
        integer_parts (List[int]): List of integer-place base-60 digits (most-significant first).
        fractional_parts (List[int]): List of fractional-place base-60 digits (most-significant first).
        is_negative (bool): Sign flag; will be cleared for the canonical zero representation.

    Returns:
        _SexagesimalParts: Immutable, normalized parts with fields:
            - is_negative (bool)
            - integer_part (Tuple[int, ...])
            - fractional_part (Tuple[int, ...])
    """

    # Remove leading zeros in integer part
    while len(integer_parts) > 1 and integer_parts[0] == 0:
        integer_parts.pop(0)

    # Remove trailing zeros in fractional part
    while len(fractional_parts) > 1 and fractional_parts[-1] == 0:
        fractional_parts.pop()

    # Enforce canonical representation for zero fractional part.
    # If the fractional part is empty after stripping zeros, it must be represented as [0].
    if not fractional_parts:
        fractional_parts = [0]

    # Handle zero case
    if (not integer_parts and not fractional_parts) or (all(part == 0 for part in integer_parts + fractional_parts)):
        integer_parts = [0]
        fractional_parts = [0]
        is_negative = False  # Zero is not negative

    return _SexagesimalParts(
        is_negative=is_negative, integer_part=tuple(integer_parts), fractional_part=tuple(fractional_parts)
    )
