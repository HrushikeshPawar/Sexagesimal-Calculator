import pytest
from sexagesimal_calculator.sexagesimal import Sexagesimal


# A decorator to make tests more readable by grouping related cases
@pytest.mark.parametrize(
    "input_val, expected_str, expected_parts",
    [
        # --- From int ---
        (0, "00;00", (False, (0,), (0,))),
        (1, "01;00", (False, (1,), (0,))),
        (-1, "-01;00", (True, (1,), (0,))),
        (60, "01,00;00", (False, (1, 0), (0,))),
        (3601, "01,00,01;00", (False, (1, 0, 1), (0,))),
        # --- From float ---
        (1.5, "01;30", (False, (1,), (30,))),
        (-0.25, "-00;15", (True, (0,), (15,))),
        (0.0, "00;00", (False, (0,), (0,))),
        # --- From decimal string ---
        ("1.5", "01;30", (False, (1,), (30,))),
        ("-0.25", "-00;15", (True, (0,), (15,))),
        # --- From sexagesimal string (testing normalization) ---
        ("1;30", "01;30", (False, (1,), (30,))),
        ("01;30,00", "01;30", (False, (1,), (30,))),  # trailing zero frac
        ("00,04;10", "04;10", (False, (4,), (10,))),  # leading zero int
        ("-0;15", "-00;15", (True, (0,), (15,))),
        # --- From another Sexagesimal instance ---
        (Sexagesimal("5;10"), "05;10", (False, (5,), (10,))),
    ],
)
def test_initialization_and_representation(input_val, expected_str, expected_parts):
    """Tests object creation from various types and its string representation."""
    s = Sexagesimal(input_val)

    # Test internal parts
    is_neg, int_p, frac_p = expected_parts
    assert s.is_negative == is_neg
    assert s.integer_part == int_p
    assert s.fractional_part == frac_p

    # Test string representation
    assert str(s) == expected_str

    # Test __repr__
    # A good repr should allow recreating the object
    recreated_s = eval(repr(s))
    assert recreated_s == s


def test_equality():
    """Tests the __eq__ and __ne__ methods."""
    assert Sexagesimal("1;30") == Sexagesimal(1.5)
    assert Sexagesimal(0) == Sexagesimal("0;0")
    assert Sexagesimal(-1) != Sexagesimal(1)
    assert Sexagesimal(1) != 1.0  # Should not be equal to other types


@pytest.mark.parametrize(
    "invalid_input",
    [
        "1;60",  # Part >= 60
        "60;00",  # Part >= 60
        "1,60;0",  # Part >= 60
        "1.2.3",  # Invalid decimal
        "1;30a",  # Invalid characters
        # "1,;30",  # Malformed string
    ],
)
def test_invalid_initialization(invalid_input):
    """Tests that invalid inputs raise ValueError."""
    with pytest.raises(ValueError):
        Sexagesimal(invalid_input)
