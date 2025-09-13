import pytest
from sexagesimal_calculator.sexagesimal import Sexagesimal


@pytest.mark.parametrize(
    "a_str, b_str, expected_str",
    [
        # --- Addition ---
        ("1;30", "2;15", "03;45"),  # Simple
        ("0;45", "0;30", "01;15"),  # Fractional carry
        ("59;59", "0;01", "01,00;00"),  # Integer carry
        ("1;00", "-0;30", "00;30"),  # Positive + Negative
        ("-1;00", "-0;30", "-01;30"),  # Negative + Negative
        ("10;00", "0;00", "10;00"),  # Add zero
    ],
)
def test_addition(a_str, b_str, expected_str):
    a, b = Sexagesimal(a_str), Sexagesimal(b_str)
    assert a + b == Sexagesimal(expected_str)


@pytest.mark.parametrize(
    "a_str, b_str, expected_str",
    [
        # --- Subtraction ---
        ("2;30", "1;15", "01;15"),  # Simple
        ("1;15", "0;30", "00;45"),  # Fractional borrow
        ("1,00;00", "0;01", "59;59"),  # Integer borrow
        ("1;00", "1;30", "-00;30"),  # Result is negative
        ("1;00", "-0;30", "01;30"),  # Positive - Negative
        ("-1;00", "-0;30", "-00;30"),  # Negative - Negative
        ("10;00", "0;00", "10;00"),  # Subtract zero
        ("10;00", "10;00", "00;00"),  # Result is zero
    ],
)
def test_subtraction(a_str, b_str, expected_str):
    a, b = Sexagesimal(a_str), Sexagesimal(b_str)
    assert a - b == Sexagesimal(expected_str)


@pytest.mark.parametrize(
    "a_str, b_str, expected_str",
    [
        # --- Multiplication ---
        ("2;00", "3;00", "06;00"),  # Integer only
        ("0;30", "10;00", "05;00"),  # Frac * Int
        ("0;30", "0;30", "00;15"),  # Frac * Frac
        ("1;30", "2;00", "03;00"),  # Mixed
        ("2;00", "-3;00", "-06;00"),  # Sign handling
        ("-2;00", "-3;00", "06;00"),  # Sign handling
        ("10;00", "0;00", "00;00"),  # Multiply by zero
        ("10;00", "1;00", "10;00"),  # Multiply by one
    ],
)
def test_multiplication(a_str, b_str, expected_str):
    a, b = Sexagesimal(a_str), Sexagesimal(b_str)
    assert a * b == Sexagesimal(expected_str)


@pytest.mark.parametrize(
    "a_str, b_str, expected_str",
    [
        # --- Division ---
        ("6;00", "3;00", "02;00"),  # Simple
        ("1;00", "2;00", "00;30"),  # Result is frac
        ("10;00", "3;00", "03;20"),  # Terminating frac
        # Test precision for non-terminating
        ("1;00", "3;00", "00;20"),
        ("0;00", "10;00", "00;00"),  # Divide zero
        ("10;00", "-2;00", "-05;00"),  # Sign handling
    ],
)
def test_division(a_str, b_str, expected_str):
    a, b = Sexagesimal(a_str), Sexagesimal(b_str)
    # Division might have rounding, so we test the string representation
    # with a reasonable precision assumption.
    assert str(a / b).startswith(expected_str)


def test_division_by_zero():
    """Tests that dividing by zero raises ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        Sexagesimal(1) / Sexagesimal(0)


@pytest.mark.parametrize(
    "base_str, exp, expected_str",
    [
        # --- Power ---
        ("2;00", 3, "08;00"),  # Positive exponent
        ("10;00", 1, "10;00"),  # Exponent is 1
        ("10;00", 0, "01;00"),  # Exponent is 0
        ("0;30", 2, "00;15"),  # Fractional base
        ("2;00", -1, "00;30"),  # Negative exponent
        ("2;00", -2, "00;15"),  # Negative exponent
    ],
)
def test_power(base_str, exp, expected_str):
    base = Sexagesimal(base_str)
    assert base**exp == Sexagesimal(expected_str)


def test_power_zero_base_edge_cases():
    """Tests edge cases for __pow__ with a base of 0."""
    zero = Sexagesimal(0)
    assert zero**5 == zero
    assert zero**0 == Sexagesimal(1)  # Convention: 0**0 is 1
    with pytest.raises(ZeroDivisionError):
        zero**-2
