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
        ("-0,02;00,0,0,0", "-02;00"),
    ],
)
def test_init(input_val, output_str):
    assert str(Sexagesimal(input_val)) == output_str


# Test Positive and Negative Values Input
@pytest.mark.parametrize(
    "input_val, output_str, integer_part, fractional_part, is_negative",
    [
        (1, "01;00", (1,), (0,), False),
        (-1, "-01;00", (1,), (0,), True),
        ("-1", "-01;00", (1,), (0,), True),
        ("-1.5", "-01;30", (1,), (30,), True),
        (-Sexagesimal(1), "-01;00", (1,), (0,), True),
    ],
)
def test_positive_negative(input_val, output_str, integer_part, fractional_part, is_negative):
    sexa_number = Sexagesimal(input_val)
    assert str(sexa_number) == output_str
    assert sexa_number.integer_part == integer_part
    assert sexa_number.fractional_part == fractional_part
    assert sexa_number.is_negative == is_negative


# Testing Validation Function
@pytest.mark.parametrize(
    "input_val, error_str",
    [
        ("1;60", "Fraction Part has a value greater than 60"),
        ("0;59,59,61", "Fraction Part has a value greater than 60"),
        ("1;59, 60, 59", "Fraction Part has a value greater than 60"),
        ("61;60", "Integer Part has a value greater than 60"),
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
        # positive + positive with multi-place fractional carries
        ("01;30,45", "02;40,30", "04;11,15"),
        # carry propagates through fractional and all integer places (creates new high-order integer place)
        ("59,59;59,59", "00,00;00,01", "01,00,00;00"),
        # mixed integer/fractional carries across multiple positions
        ("10,59;59,30", "00,01;00,40", "11,01;00,10"),
        # positive + negative (positive magnitude larger)
        ("05;20,10", "-02;45,50", "02;34,20"),
        # negative + positive (negative magnitude larger)
        ("-10;00,00", "02;30,30", "-07;29,30"),
        # negative + negative (both negative, carries in fractions)
        ("-03;20,20", "-01;50,50", "-05;11,10"),
        # exact cancellation -> zero
        ("03;10,10", "-03;10,10", "00;00"),
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
        # fractional borrow across multiple fractional places
        ("01;00,00", "00;59,59", "00;00,01"),
        # borrow propagates through fractional and all integer places (reduces high-order integer)
        ("01,00;00,00", "00,00;00,01", "59;59,59"),
        # positive - negative = addition (cross-sign behavior)
        ("05;20,10", "-02;45,50", "08;06"),
        # negative - positive (becomes more negative)
        ("-10;00,00", "02;30,30", "-12;30,30"),
        # negative - negative (subtracting a negative makes value less negative)
        ("-03;20,20", "-01;50,50", "-01;29,30"),
        # exact cancellation -> zero
        ("03;10,10", "03;10,10", "00;00"),
        # result becomes negative when subtrahend is larger
        ("02;00,00", "03;00,00", "-01;00"),
        # deep fractional borrow with three fractional places
        ("01;00,00,00", "00;59,59,59", "00;00,00,01"),
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
