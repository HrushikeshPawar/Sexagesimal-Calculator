from sexagesimal_calculator.sexagesimal import Sexagesimal
import pytest


# Initialization Test
@pytest.mark.parametrize(
    "input_val, output_str",
    [
        (0, "00;00"),
        ("0", "00;00"),
        ("-0", "00;00"),
        (0.0, "00;00"),
        ("0.0", "00;00"),
        ("-0.0", "00;00"),
        (0.5, "00;30"),
        ("0.25", "00;15"),
        (-2, "-02;00"),
        ("-2", "-02;00"),
        ("-2;0", "-02;00"),
        ("-02;00", "-02;00"),
    ],
)
def test_init(input_val, output_str):
    assert str(Sexagesimal(input_val)) == output_str


# Test Positive and Negative Values Input
@pytest.mark.parametrize(
    "input_val, S_value, output_str, is_negative",
    [
        (1, "01;00", "01;00", False),
        (-1, "01;00", "-01;00", True),
        ("-1", "01;00", "-01;00", True),
        ("-1.5", "01;30", "-01;30", True),
        (-Sexagesimal(1), "01;00", "-01;00", True),
    ],
)
def test_positive_negative(input_val, S_value, output_str, is_negative):
    sexa_number = Sexagesimal(input_val)
    assert sexa_number.S == S_value
    assert str(sexa_number) == output_str
    assert sexa_number.negative == is_negative


# Testing Validation Function
@pytest.mark.parametrize(
    "input_val, error_str",
    [
        ("1;60", "Fraction Part has a value greater than 60"),
        ("0;59,59,61", "Fraction Part has a value greater than 60"),
        ("1;59, 60, 59", "Fraction Part has a value greater than 60"),
        ("61;60", "Fraction Part has a value greater than 60"),
    ],
)
def test_is_valid(input_val, error_str):
    with pytest.raises(ValueError) as excinfo:
        Sexagesimal(input_val)

    assert error_str in str(excinfo.value)


# Testing Addition Value Inputs
@pytest.mark.parametrize(
    "input_val1, input_val2, output_str",
    [
        (1, 1, "02;00"),
        (1, -1, "00;00"),
        (-1, 1, "00;00"),
        (-1, -1, "-02;00"),
        (1, 1.5, "02;30"),
        (1, -1.5, "-00;30"),
        (0, 0, "00;00"),
    ],
)
# Testing Addition Function
def test_add(input_val1, input_val2, output_str):
    assert str(Sexagesimal(input_val1) + Sexagesimal(input_val2)) == output_str


# Testing Subtraction Value Inputs
@pytest.mark.parametrize(
    "input_val1, input_val2, output_str",
    [
        (1, 1, "00;00"),
        (1, -1, "02;00"),
        (-1, 1, "-02;00"),
        (-1, -1, "00;00"),
        (1, 1.5, "-00;30"),
        (1, -1.5, "02;30"),
        (0, 0, "00;00"),
    ],
)
# Testing Subtraction Function
def test_sub(input_val1, input_val2, output_str):
    assert str(Sexagesimal(input_val1) - Sexagesimal(input_val2)) == output_str


# Testing Multiplication Value Inputs
@pytest.mark.parametrize(
    "input_val1, input_val2, output_str",
    [
        (1, 1, "01;00"),
        (1, -1, "-01;00"),
        (-1, 1, "-01;00"),
        (-1, -1, "01;00"),
        (0, 1, "00;00"),
        (0, -1, "00;00"),
        (-1, 0, "00;00"),
        (1, 0, "00;00"),
        (1, 1.5, "01;30"),
        (1, -1.5, "-01;30"),
        (0, 0, "00;00"),
    ],
)
# Testing Multiplication Function
def test_mul(input_val1, input_val2, output_str):
    assert str(Sexagesimal(input_val1) * Sexagesimal(input_val2)) == output_str


# Testing Division Value Inputs
@pytest.mark.parametrize(
    "input_val1, input_val2, output_str",
    [
        (1, 1, "01;00"),
        (1, -1, "-01;00"),
        (-1, 1, "-01;00"),
        (-1, -1, "01;00"),
        (0, 1, "00;00"),
        (0, -1, "00;00"),
        (2, 1, "02;00"),
        (2, -1, "-02;00"),
        (-2, 1, "-02;00"),
        (-2, -1, "02;00"),
    ],
)
# Testing Division Function
def test_div(input_val1, input_val2, output_str):
    assert str(Sexagesimal(input_val1) / Sexagesimal(input_val2)) == output_str
