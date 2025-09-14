import pytest
from sexagesimal_calculator.sexagesimal import Sexagesimal


@pytest.mark.parametrize(
    "s1_str, s2_str, expected",
    [
        # --- Greater Than ---
        ("1;0", "0;59", True),  # Different integer part
        ("-0;59", "-1;0", True),  # Different integer part (negative)
        ("1;1", "1;0", True),  # Different fractional part
        ("1;0", "0;0", True),  # Positive vs Zero
        ("0;0", "-1;0", True),  # Zero vs Negative
        ("1;0", "-1;0", True),  # Positive vs Negative
    ],
)
def test_greater_than(s1_str, s2_str, expected):
    s1, s2 = Sexagesimal(s1_str), Sexagesimal(s2_str)
    assert (s1 > s2) == expected


@pytest.mark.parametrize(
    "s1_str, s2_str, expected",
    [
        # --- Less Than ---
        ("0;59", "1;0", True),  # Different integer part
        ("-1;0", "-0;59", True),  # Different integer part (negative)
        ("1;0", "1;1", True),  # Different fractional part
        ("-1;0", "0;0", True),  # Negative vs Zero
        ("0;0", "1;0", True),  # Zero vs Positive
        ("-1;0", "1;0", True),  # Negative vs Positive
    ],
)
def test_less_than(s1_str, s2_str, expected):
    s1, s2 = Sexagesimal(s1_str), Sexagesimal(s2_str)
    assert (s1 < s2) == expected


@pytest.mark.parametrize(
    "s1_str, s2_str, expected",
    [
        ("1;0", "1;0", True),
        ("1;1", "1;0", True),
        ("-0;59", "-1;0", True),
    ],
)
def test_greater_equal(s1_str, s2_str, expected):
    s1, s2 = Sexagesimal(s1_str), Sexagesimal(s2_str)
    assert (s1 >= s2) == expected


@pytest.mark.parametrize(
    "s1_str, s2_str, expected",
    [
        ("1;0", "1;0", True),
        ("1;0", "1;1", True),
        ("-1;0", "-0;59", True),
    ],
)
def test_less_equal(s1_str, s2_str, expected):
    s1, s2 = Sexagesimal(s1_str), Sexagesimal(s2_str)
    assert (s1 <= s2) == expected
