from typing import List, Union
from decimal import Decimal
from sexagesimal_calculator.sexagesimal import Sexagesimal


def increment_table(
    initial: Union[str, int, float], increment: Union[str, int, float], rows: int = 10, mod: int = 0
) -> List[str]:
    """Generates a table of incrementing sexagesimal values."""
    current_val = Sexagesimal(initial)
    increment_val = Sexagesimal(increment)

    table = []
    for _ in range(rows + 1):  # Include the initial value
        table.append(str(current_val))
        current_val += increment_val

        if mod > 1:
            dec_val = current_val.to_decimal()
            int_part = int(dec_val)
            frac_part = dec_val - int_part
            new_int = int_part % mod
            current_val = Sexagesimal(str(Decimal(new_int) + frac_part))

    return table
