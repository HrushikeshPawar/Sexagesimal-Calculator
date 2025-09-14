from sexagesimal_calculator.sexagesimal import Sexagesimal


def test_negation():
    """Tests the __neg__ method."""
    assert -Sexagesimal("5;30") == Sexagesimal("-5;30")
    assert -Sexagesimal("-5;30") == Sexagesimal("5;30")
    assert -Sexagesimal(0) == Sexagesimal(0)


def test_absolute_value():
    """Tests the __abs__ method."""
    assert abs(Sexagesimal("5;30")) == Sexagesimal("5;30")
    assert abs(Sexagesimal("-5;30")) == Sexagesimal("5;30")
    assert abs(Sexagesimal(0)) == Sexagesimal(0)
