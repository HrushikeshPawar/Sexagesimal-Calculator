from sympy import Rational
from typing import List, TYPE_CHECKING
from decimal import Decimal, InvalidOperation, getcontext

from sexagesimal_calculator.core import BASE, PART_SEP, VAL_SEP, _SexagesimalParts
from sexagesimal_calculator.utils import _normalize_parts

if TYPE_CHECKING:
    from sexagesimal_calculator.sexagesimal import Sexagesimal


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
    try:
        # Use Decimal for high precision and to handle scientific notation
        getcontext().prec = accuracy + 20  # Set precision
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


def _to_rational(sexagesimal: "Sexagesimal") -> Rational:
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


def _rational_to_sexagesimal_parts(num: Rational, max_frac_places: int = 80) -> _SexagesimalParts:
    """
    Convert a sympy.Rational to normalized sexagesimal parts.

    Summary:
        Produce a canonical _SexagesimalParts representation for the given exact
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
        _SexagesimalParts: Immutable, normalized parts with fields:
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
        return _SexagesimalParts(is_negative=False, integer_part=(0,), fractional_part=(0,))

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

    return _normalize_parts(integer_parts, fractional_parts, is_negative)
