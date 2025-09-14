# In test/test_06_utils.py

import pytest

# We import the function directly from its new home in the utils module
from sexagesimal_calculator.utils import increment_table


@pytest.mark.parametrize(
    "initial, increment, rows, expected_output",
    [
        (
            1,
            1,
            3,
            ["01;00", "02;00", "03;00", "04;00"],
        ),
        (
            "0;45",
            "0;30",
            2,
            ["00;45", "01;15", "01;45"],
        ),
        (
            "2;00",
            "-0;30",
            4,
            ["02;00", "01;30", "01;00", "00;30", "00;00"],
        ),
        (
            -2,
            0.5,
            4,
            ["-02;00", "-01;30", "-01;00", "-00;30", "00;00"],
        ),
    ],
    ids=[
        "simple-positive-integers",
        "fractional-carry-over",
        "negative-increment",
        "negative-initial-with-float-increment",
    ],
)
def test_increment_table_no_modulo(initial, increment, rows, expected_output):
    """Tests the increment_table function without using the 'mod' parameter."""
    result = increment_table(initial=initial, increment=increment, rows=rows, mod=0)
    assert result == expected_output


@pytest.mark.parametrize(
    "initial, increment, rows, mod, expected_output",
    [
        (
            58,
            1,
            3,
            60,
            ["58;00", "59;00", "00;00", "01;00"],
        ),
        (
            "59;30",
            "1;00",
            2,
            60,
            ["59;30", "00;30", "01;30"],
        ),
        (
            8,
            1,
            3,
            10,
            ["08;00", "09;00", "00;00", "01;00"],
        ),
        (
            "9;45",
            "0;30",  # Increment will cause integer part to change
            3,
            10,
            # 9;45 -> 10;15 -> mod(10) -> 0;15 -> 0;45 -> 1;15
            ["09;45", "00;15", "00;45", "01;15"],
        ),
    ],
    ids=[
        "simple-wrap-around-at-60",
        "wrap-around-preserves-fractional-part",
        "wrap-around-with-smaller-modulus",
        "wrap-around-triggered-by-fractional-carry",
    ],
)
def test_increment_table_with_modulo(initial, increment, rows, mod, expected_output):
    """Tests the increment_table function with the 'mod' parameter active."""
    result = increment_table(initial=initial, increment=increment, rows=rows, mod=mod)
    assert result == expected_output


@pytest.mark.parametrize(
    "initial, increment, rows, expected_output",
    [
        (
            10,
            1,
            0,
            ["10;00"],
        ),
        (
            5,
            0,
            3,
            ["05;00", "05;00", "05;00", "05;00"],
        ),
        (
            0,
            "1;15",
            2,
            ["00;00", "01;15", "02;30"],
        ),
    ],
    ids=[
        "zero-rows-returns-initial-value-only",
        "zero-increment-returns-repeating-values",
        "zero-initial-value",
    ],
)
def test_increment_table_edge_cases(initial, increment, rows, expected_output):
    """Tests edge cases like zero rows or a zero increment value."""
    result = increment_table(initial=initial, increment=increment, rows=rows)
    assert result == expected_output
