# In tests/test_05_rounding.py

import pytest
from sexagesimal_calculator.sexagesimal import Sexagesimal


# We use parametrize to test a wide range of inputs and expected outputs declaratively.
# The `ids` parameter gives each test case a human-readable name for easier debugging.
@pytest.mark.parametrize(
    "input_str, precision, expected_str",
    [
        # --- Basic Round Down ---
        ("10;14,29", 1, "10;14"),
        ("-10;14,29", 1, "-10;14"),
        ("10;14,22,59", 1, "10;14"),
        # --- Basic Round Up (at the threshold) ---
        ("10;14,30", 1, "10;15"),
        ("-10;14,30", 1, "-10;15"),
        ("10;14,59,59", 1, "10;15"),
        # --- Rounding to Integer (precision=0) ---
        ("12;29,59", 0, "12;00"),
        ("12;30,00", 0, "13;00"),
        ("-12;29,59", 0, "-12;00"),
        ("-12;30,00", 0, "-13;00"),
    ],
    ids=[
        "positive-down",
        "negative-down",
        "positive-down-long",
        "positive-up-threshold",
        "negative-up-threshold",
        "positive-up-long",
        "to-integer-down",
        "to-integer-up",
        "to-integer-neg-down",
        "to-integer-neg-up",
    ],
)
def test_round_basic_cases(input_str: str, precision: int, expected_str: str):
    """Tests the fundamental rounding logic (up, down, positive, negative)."""
    s_input = Sexagesimal(input_str)
    s_expected = Sexagesimal(expected_str)

    result = s_input.round(precision)

    assert result == s_expected


@pytest.mark.parametrize(
    "input_str, expected_str",
    [
        # Tests that the default precision is 0
        ("12;29", "12;00"),
        ("12;30", "13;00"),
        ("-12;59", "-13;00"),
    ],
    ids=[
        "default-down",
        "default-up",
        "default-neg-up",
    ],
)
def test_round_default_precision(input_str: str, expected_str: str):
    """Tests that the default precision for round() is 0."""
    s_input = Sexagesimal(input_str)
    s_expected = Sexagesimal(expected_str)

    # Call round() with no arguments
    result = s_input.round()

    assert result == s_expected


@pytest.mark.parametrize(
    "input_str, precision, expected_str",
    [
        # --- Fractional Cascade ---
        ("10;59,30", 1, "11;00"),
        ("-10;59,30", 1, "-11;00"),
        ("10;14,59,30", 2, "10;15,00"),
        # --- Integer Cascade ---
        ("59;59,30", 0, "01,00;00"),
        ("-59;59,30", 0, "-01,00;00"),
        # --- The Ultimate Cascade Stress Test ---
        ("1,59,59;59,59,30", 2, "02,00,00;00,00"),
    ],
    ids=[
        "frac-cascade-pos",
        "frac-cascade-neg",
        "mid-frac-cascade",
        "int-cascade-pos",
        "int-cascade-neg",
        "long-cascade",
    ],
)
def test_round_cascading_carry(input_str: str, precision: int, expected_str: str):
    """Tests that rounding up correctly cascades carries through all places."""
    s_input = Sexagesimal(input_str)
    s_expected = Sexagesimal(expected_str)

    result = s_input.round(precision)

    assert result == s_expected


@pytest.mark.parametrize(
    "input_str, precision, expected_str",
    [
        # Rounding to more places than exist should do nothing
        ("10;15,30", 5, "10;15,30"),
        # Rounding a number with no fractional part
        ("10;00", 2, "10;00"),
        # Rounding the number zero
        ("0;00", 3, "00;00"),
        # Rounding a number that is exactly at the rounding boundary
        ("10;15", 2, "10;15"),
    ],
    ids=[
        "precision-too-high",
        "no-fractional-part",
        "rounding-zero",
        "exact-precision",
    ],
)
def test_round_edge_cases(input_str: str, precision: int, expected_str: str):
    """Tests edge cases like rounding zero or rounding to excess precision."""
    s_input = Sexagesimal(input_str)
    s_expected = Sexagesimal(expected_str)

    result = s_input.round(precision)

    assert result == s_expected


def test_round_invalid_input():
    """Tests that the round method raises appropriate errors for invalid input."""
    s = Sexagesimal("10;30")

    # Precision must be a non-negative integer.
    with pytest.raises(ValueError, match="Precision must be a non-negative integer."):
        s.round(-1)

    # Precision must be an integer
    with pytest.raises(TypeError):
        s.round(1.5)  # type: ignore
