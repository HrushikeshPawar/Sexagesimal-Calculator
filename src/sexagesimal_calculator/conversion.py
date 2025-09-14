from sympy import Rational
from typing import List, TYPE_CHECKING
from decimal import Decimal, InvalidOperation, localcontext

from sexagesimal_calculator.core import BASE, PART_SEP, VAL_SEP, SexagesimalParts

if TYPE_CHECKING:
    from sexagesimal_calculator.sexagesimal import Sexagesimal


def normalize_parts(integer_parts: List[int], fractional_parts: List[int], is_negative: bool) -> SexagesimalParts:
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
        - The function returns a frozen SexagesimalParts dataclass suitable for storage
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
        SexagesimalParts: Immutable, normalized parts with fields:
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

    return SexagesimalParts(
        is_negative=is_negative, integer_part=tuple(integer_parts), fractional_part=tuple(fractional_parts)
    )


# Convert the given Decimal Number to Sexagesimal
def from_decimal_str(value_str: str, accuracy: int = 80) -> str:
    """
    Converts a decimal number string into a sexagesimal string.

    This method is designed to be robust and can handle standard decimal
    notation ("1.5") as well as scientific notation ("1.5e-2").

    Args:
        value_str (str): The string representation of the decimal number.
        accuracy (int): The number of fractional places to compute.

    Returns:
        str: A string in the canonical "integer;fractional" format,
            e.g., "01;30".
    """
    with localcontext() as ctx:
        ctx.prec = accuracy + 20  # Set precision higher than needed to avoid rounding issues
        try:
            # Use Decimal for high precision and to handle scientific notation
            num = Decimal(value_str)
        except InvalidOperation:
            raise ValueError(f"Could not parse '{value_str}' as a decimal number.")

    # Separate integer and fractional parts of the Decimal
    integer_part = int(num.to_integral_value(rounding="ROUND_DOWN"))
    fractional_part = num - Decimal(integer_part)

    # Convert integer part to a list of base-60 digits
    int_places = []
    if integer_part == 0:
        int_places = [0]
    else:
        temp_int = abs(integer_part)
        while temp_int > 0:
            int_places.insert(0, temp_int % BASE)
            temp_int //= BASE

    # Convert fractional part to a list of base-60 digits
    frac_places = []
    temp_frac = abs(fractional_part)
    for _ in range(accuracy):
        if temp_frac == 0:
            break
        temp_frac *= BASE
        digit = int(temp_frac)
        frac_places.append(digit)
        temp_frac -= Decimal(digit)

    # Format the lists into the final sexagesimal string
    int_str = VAL_SEP.join(map(str, int_places)) if int_places else "0"
    frac_str = VAL_SEP.join(map(str, frac_places)) if frac_places else "0"

    return f"{int_str}{PART_SEP}{frac_str}"


def to_rational(sexagesimal: "Sexagesimal") -> Rational:
    """
    Convert the internal sexagesimal representation to an exact sympy.Rational.

    Summary:
        Build an exact Rational by summing the integer-place digits weighted by
        BASE**k (k = 0,1,2,...) and the fractional-place digits as digit/BASE**k
        (k = 1,2,...). The sign of the result matches the instance sign; zero is
        returned as a non-negative Rational.

    Args:
        sexagesimal (Sexagesimal): The Sexagesimal instance to convert.

    Returns:
        Rational: Exact rational value equivalent to this sexagesimal number.

    Notes:
        - Uses sympy.Rational for exact fractional arithmetic.
        - Integer and fractional contributions are accumulated separately.
        - The implementation preserves exactness (no floating-point rounding).
    """

    total = Rational(0)

    # Sum of integer digits
    for idx, digit in enumerate(reversed(sexagesimal.integer_part)):
        total += digit * pow(BASE, idx)  # type: ignore

    # Sum of fractional digits
    for idx, digit in enumerate(sexagesimal.fractional_part, start=1):
        total += Rational(digit, pow(BASE, idx))  # type: ignore

    return -total if sexagesimal.is_negative else total  # type: ignore


def rational_to_sexagesimal_parts(num: Rational, max_frac_places: int = 80) -> SexagesimalParts:
    """
    Convert a sympy.Rational to normalized sexagesimal parts.

    Summary:
        Produce a canonical SexagesimalParts representation for the given exact
        Rational `num`. The function extracts the integer portion as base-60
        digits and generates up to `max_frac_places` fractional base-60 digits
        by repeatedly multiplying the fractional remainder by BASE. The result
        is normalized (no extraneous leading integer zeros or trailing
        fractional zeros) and preserves the sign of the input; zero is returned
        using the canonical non-negative representation.

    Args:
        num (Rational): Exact rational value to convert.
        max_frac_places (int, optional): Maximum number of fractional base-60
            digits to produce. Conversion stops early if the fractional part
            terminates. Defaults to 80.

    Returns:
        SexagesimalParts: Immutable, normalized parts with fields:
            - is_negative (bool)
            - integer_part (Tuple[int, ...])
            - fractional_part (Tuple[int, ...])

    Notes:
        - Uses exact Rational arithmetic; no floating-point rounding is used.
        - If the sexagesimal expansion is non-terminating the result is a
            truncated expansion of at most `max_frac_places` digits.
        - Callers may increase `max_frac_places` to reduce truncation error.
    """

    if num == 0:
        return SexagesimalParts(is_negative=False, integer_part=(0,), fractional_part=(0,))

    is_negative: bool = num < 0
    abs_num: Rational = abs(num)

    # Step 1: Calculate integer part and convert to base-<BASE> tuple
    integer_val = int(abs_num)
    integer_parts: List[int] = []

    if integer_val == 0:
        integer_parts.append(0)
    else:
        while integer_val > 0:
            integer_parts.insert(0, integer_val % BASE)
            integer_val //= BASE

    # Step 2: Calculate fractional part, using remainder
    remainder: Rational = abs_num - int(abs_num)  # type: ignore
    fractional_parts: List[int] = []

    for _ in range(max_frac_places):
        remainder *= BASE  # type: ignore
        frac_digit = int(remainder)
        fractional_parts.append(frac_digit)
        remainder -= frac_digit  # type: ignore

        if remainder == 0:
            break

    return normalize_parts(integer_parts, fractional_parts, is_negative)
