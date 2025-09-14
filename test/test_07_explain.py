# In test/test_07_explain.py
from sexagesimal_calculator import Sexagesimal
from sexagesimal_calculator.explain import (
    explain_addition,
    explain_subtraction,
    explain_multiplication,
    explain_division,
)


def test_explain_addition():
    """Tests that explain_addition's result matches the real result."""
    a, b = Sexagesimal("59;30"), Sexagesimal("1;45")
    explanation = explain_addition(a, b)

    # Crucial Test: The explained result MUST match the operator's result.
    assert explanation.result == a + b

    # Test that the narrative is being generated.
    explanation_str = str(explanation)
    assert "Addition of 59;30 + 01;45" in explanation_str
    assert "Final Result: 01,01;15" in explanation_str


def test_explain_addition_delegates_to_subtraction():
    """Tests that the addition explanation correctly shows delegation to subtraction."""
    a, b = Sexagesimal("10;00"), Sexagesimal("-5;30")
    explanation_str = str(explain_addition(a, b))

    assert "Addition of 10;00 + -05;30" in explanation_str
    assert "delegates to subtraction" in explanation_str
    assert "Operation becomes: A - B" in explanation_str
    # Check that the final result is correct
    assert "Final Result: 04;30" in explanation_str


def test_explain_subtraction_delegates_to_addition():
    """Tests that the subtraction explanation correctly shows delegation to addition."""
    a, b = Sexagesimal("10;00"), Sexagesimal("-5;30")
    explanation_str = str(explain_subtraction(a, b))

    assert "Subtraction of 10;00 - -05;30" in explanation_str
    assert "delegates to addition" in explanation_str
    assert "Operation becomes: A + B" in explanation_str
    assert "Final Result: 15;30" in explanation_str


def test_explain_subtraction():
    """Tests that explain_subtraction's result matches the real result."""
    a, b = Sexagesimal("10;15"), Sexagesimal("5;30")
    explanation = explain_subtraction(a, b)
    assert explanation.result == a - b

    explanation_str = str(explanation)
    assert "Subtraction of 10;15 - 05;30" in explanation_str
    assert "Final Result: 04;45" in explanation_str


def test_explain_multiplication():
    """Tests that explain_multiplication's result matches the real result."""
    a, b = Sexagesimal("1;15"), Sexagesimal("2;30")
    explanation = explain_multiplication(a, b)
    assert explanation.result == a * b

    explanation_str = str(explanation)
    assert "Long Multiplication of 01;15 * 02;30" in explanation_str
    assert "Final Result: 03;07,30" in explanation_str


def test_explain_division():
    """Tests that explain_division's result matches the real result."""
    a, b = Sexagesimal("10;00"), Sexagesimal("4;00")
    explanation = explain_division(a, b)
    assert explanation.result == a / b

    explanation_str = str(explanation)
    assert "Division of 10;00 / 04;00" in explanation_str
    assert "Final Result: 02;30" in explanation_str


def test_explain_subtraction_both_negative():
    """Tests that subtracting two negatives delegates to a positive subtraction."""
    a, b = Sexagesimal("-10;00"), Sexagesimal("-5;30")
    explanation_str = str(explain_subtraction(a, b))

    assert "equivalent to B - A" in explanation_str
    assert "Final Result: -04;30" in explanation_str


def test_explain_division_by_zero():
    """Tests the explanation for division by zero."""
    a, b = Sexagesimal("10;00"), Sexagesimal(0)
    explanation_str = str(explain_division(a, b))

    assert "Cannot divide by zero" in explanation_str
