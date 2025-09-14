from decimal import Decimal, InvalidOperation, getcontext

from sexagesimal_calculator.contants import BASE, PART_SEP, VAL_SEP


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
