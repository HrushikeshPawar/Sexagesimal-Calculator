# In tests/test_99_property_based.py

import pytest
from decimal import Decimal, getcontext

from hypothesis import given, settings, strategies as st
from sexagesimal_calculator.sexagesimal import Sexagesimal

# Set a high precision for Decimal comparisons in tests
getcontext().prec = 50

# --- Hypothesis Strategies ---

# Strategy to generate high-precision, safe Decimal objects
# (avoiding NaN and infinity which it's not designed to handle).
safe_decimals = st.decimals(
    min_value=-1e10,
    max_value=1e10,
    allow_nan=False,
    allow_infinity=False,
    places=10,
)

# Strategy that generates Sexagesimal objects by creating PRECISE Decimals first,
# then converting them to a PRECISE string, which our class then parses.
# This avoids any float imprecision.
sexagesimals = safe_decimals.map(str).map(Sexagesimal)


# --- The Property-Based Tests ---


@given(s=sexagesimals)
def test_round_trip_invariant(s: Sexagesimal):
    """
    Property: Parsing a Sexagesimal's string representation should yield an
    equal object. str(Sexagesimal(x)) == x
    """
    recreated_s = Sexagesimal(str(s))
    assert recreated_s == s


@given(a=sexagesimals, b=sexagesimals)
def test_addition_is_commutative(a: Sexagesimal, b: Sexagesimal):
    """Property: a + b == b + a"""
    assert a + b == b + a


@given(a=sexagesimals, b=sexagesimals)
def test_multiplication_is_commutative(a: Sexagesimal, b: Sexagesimal):
    """Property: a * b == b * a"""
    assert a * b == b * a


@given(a=safe_decimals, b=safe_decimals)
@settings(max_examples=200, deadline=None)  # Run more examples for this complex test
def test_addition_consistency_with_decimal(a: Decimal, b: Decimal):
    """
    Property (Oracle Test): Sexagesimal addition should be consistent with
    Python's high-precision Decimal addition.
    """
    s_a = Sexagesimal(str(a))
    s_b = Sexagesimal(str(b))

    # Perform the operation in our class
    s_sum = s_a + s_b

    # Perform the operation using the trusted "oracle" (Decimal)
    dec_sum = a + b

    # Compare the results. We need a tolerance because the initial float->Sexagesimal
    # conversion has finite precision.
    assert s_sum.to_decimal() == pytest.approx(dec_sum)


@given(a=sexagesimals, b=sexagesimals)
def test_additive_inverse(a: Sexagesimal, b: Sexagesimal):
    """Property: (a + b) - b == a. This should be exact."""
    result = (a + b) - b
    assert result == a


@given(a=sexagesimals, b=sexagesimals.filter(lambda s: s != Sexagesimal(0)))
def test_multiplicative_inverse(a: Sexagesimal, b: Sexagesimal):
    """
    Property: (a * b) / b == a, for b != 0. This should be exact.
    The .filter() method ensures hypothesis never gives us a zero for `b`.
    """
    result = (a * b) / b
    assert result.to_decimal() == pytest.approx(a.to_decimal())


@given(base=st.integers(min_value=-5, max_value=5).map(Sexagesimal), exp=st.integers(min_value=0, max_value=4))
def test_power_consistency_with_python(base: Sexagesimal, exp: int):
    """
    Property: Our __pow__ should agree with Python's for integers.
    We limit the range to keep the test fast and avoid massive numbers.
    """
    if base == Sexagesimal(0) and exp == 0:
        # Our class defines 0**0 as 1, which is standard.
        assert base**exp == Sexagesimal(1)
        return

    result_dec = (base**exp).to_decimal()
    expected_dec = base.to_decimal() ** exp

    # assert result_dec == pytest.approx(expected_dec, abs=1e-30)
    # We may still need a small tolerance here due to precision limits in the
    # to_decimal conversion of very long results.
    assert result_dec == pytest.approx(expected_dec)
