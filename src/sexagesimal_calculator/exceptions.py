# In src/sexagesimal_calculator/exceptions.py
class SexagesimalError(Exception):
    """Base class for all exceptions in this library."""

    pass


class InvalidFormatError(SexagesimalError, ValueError):
    """Raised when a string cannot be parsed as a sexagesimal number."""

    pass
