import pytest
import operator
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


@pytest.mark.parametrize(
    "initial_str, addend_str, expected_str",
    [
        ("1;30", "0;30", "02;00"),  # Simple case
        ("0;59", "0;01", "01;00"),  # Fractional carry
        ("59;59", "0;01", "01,00;00"),  # Integer cascade
        ("10;00", "-2;30", "07;30"),  # Adding a negative
        ("-10;00", "2;30", "-07;30"),  # Adding to a negative
        ("10;00", "0;00", "10;00"),  # Adding zero
    ],
    ids=[
        "simple",
        "frac-carry",
        "int-cascade",
        "add-negative",
        "add-to-negative",
        "add-zero",
    ],
)
def test_iadd(initial_str, addend_str, expected_str):
    """Tests the in-place addition method (+=)."""
    s = Sexagesimal(initial_str)
    addend = Sexagesimal(addend_str)

    # Perform the in-place operation
    s += addend

    assert s == Sexagesimal(expected_str)


@pytest.mark.parametrize(
    "initial_str, subtrahend_str, expected_str",
    [
        ("2;30", "0;30", "02;00"),  # Simple case
        ("1;00", "0;01", "00;59"),  # Fractional borrow
        ("1,00;00", "0;01", "59;59"),  # Integer cascade
        ("10;00", "-2;30", "12;30"),  # Subtracting a negative
        ("-10;00", "2;30", "-12;30"),  # Subtracting from a negative
        ("10;00", "0;00", "10;00"),  # Subtracting zero
        ("5;15", "5;15", "00;00"),  # Subtracting to zero
    ],
    ids=[
        "simple",
        "frac-borrow",
        "int-cascade",
        "sub-negative",
        "sub-from-negative",
        "sub-zero",
        "sub-to-zero",
    ],
)
def test_isub(initial_str, subtrahend_str, expected_str):
    """Tests the in-place subtraction method (-=)."""
    s = Sexagesimal(initial_str)
    subtrahend = Sexagesimal(subtrahend_str)

    # Perform the in-place operation
    s -= subtrahend

    assert s == Sexagesimal(expected_str)


@pytest.mark.parametrize(
    "initial_str, multiplier_str, expected_str",
    [
        ("2;30", "2;00", "05;00"),  # Simple case
        ("1;15", "0;30", "00;37,30"),  # Fractional multiplication
        ("10;00", "-2;00", "-20;00"),  # Multiplying by a negative
        ("-10;00", "2;00", "-20;00"),  # Multiplying a negative
        ("10;00", "0;00", "00;00"),  # Multiplying by zero
        ("10;00", "1;00", "10;00"),  # Multiplying by one
        ("10;00", "-1;00", "-10;00"),  # Multiplying by negative one
    ],
    ids=[
        "simple",
        "fractional",
        "mul-by-negative",
        "mul-a-negative",
        "mul-by-zero",
        "mul-by-one",
        "mul-by-neg-one",
    ],
)
def test_imul(initial_str, multiplier_str, expected_str):
    """Tests the in-place multiplication method (*=)."""
    s = Sexagesimal(initial_str)
    multiplier = Sexagesimal(multiplier_str)

    # Perform the in-place operation
    s *= multiplier

    assert s == Sexagesimal(expected_str)


@pytest.mark.parametrize(
    "op, op_symbol",
    [
        (operator.iadd, "+="),
        (operator.isub, "-="),
        (operator.imul, "*="),
    ],
    ids=["iadd", "isub", "imul"],
)
def test_inplace_operators_return_new_instance(op, op_symbol):
    """
    Tests that the in-place operators return a new object instance,
    which is the correct behavior for immutable classes.
    """
    s = Sexagesimal("10;00")
    other = Sexagesimal("1;00")

    # Store the memory ID of the original object
    initial_id = id(s)

    # Perform the "in-place" operation. The `op` function here is equivalent
    # to writing `s += other`, `s -= other`, etc.
    s = op(s, other)

    # Store the memory ID of the object after the operation
    final_id = id(s)

    # For an immutable object, the ID MUST be different.
    assert initial_id != final_id, f"Object ID should change after {op_symbol}"
