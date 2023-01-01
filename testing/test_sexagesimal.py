from sexagesimal_calculator.sexagesimal import Sexagesimal
import pytest


# Initialization Test
@pytest.mark.parametrize("input_val, output_str", [
    (0, "00;00"),
    ("0", "00;00"),
    (0.0, "00;00"),
    ("0.0", "00;00"),
    (0.5, "00;30"),
    ("0.25", "00;15"),
])
def test_init(input_val, output_str):

    assert str(Sexagesimal(input_val)) == output_str


# Test Positive and Negative Values Input
@pytest.mark.parametrize("input_val, S_value, output_str, is_negative", [
    (1, "01;00", "01;00", False),
    (-1, "01;00", "-01;00", True),
    ("-1", "01;00", "-01;00", True),
    ("-1.5", "01;30", "-01;30", True),
])
def test_positive_negative(input_val, S_value, output_str, is_negative):
    sexa_number = Sexagesimal(input_val)
    assert sexa_number.S == S_value
    assert str(sexa_number) == output_str
    assert sexa_number.negative == is_negative


# Testing Validation Function
@pytest.mark.parametrize("input_val, error_str", [
    ('1;60', 'Fraction Part has a value greater than 60'),
    ('0;59,59,61', 'Fraction Part has a value greater than 60'),
    ('1;59, 60, 59', 'Fraction Part has a value greater than 60'),
    ('61;60', 'Fraction Part has a value greater than 60'),
])
def test_is_valid(input_val, error_str):
    with pytest.raises(ValueError) as excinfo:
        Sexagesimal(input_val)

    assert error_str in str(excinfo.value)
