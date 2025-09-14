# Imports
from typing import Tuple, Union
from decimal import Decimal, localcontext

from sympy import Rational

from sexagesimal_calculator import conversion
from sexagesimal_calculator import arithmetic

from sexagesimal_calculator.core import BASE, PART_SEP, VAL_SEP, SexagesimalParts
from sexagesimal_calculator.exceptions import InvalidFormatError


# The Sexagesimal class
class Sexagesimal:
    """
    Represents an immutable sexagesimal (base-60) number.

    This class provides a robust way to handle sexagesimal numbers, which are
    common in historical mathematics and astronomy. It supports standard
    arithmetic operations while ensuring that all calculations are performed
    natively in base-60.

    Instances of this class are immutable. All arithmetic operations return a
    new `Sexagesimal` instance.

    Args:
        value (Union[str, int, float, Sexagesimal]): The value to initialize
            the number with.
            - If str: Can be a decimal ('1.5') or sexagesimal ('01;30').
            - If int or float: Will be converted from decimal.
            - If Sexagesimal: A new instance is created from the provided one.

    Attributes:
        is_negative (bool): True if the number is negative.
        integer_part (Tuple[int, ...]): A tuple representing the integer
            places of the number. For 123;45 (2,3;45), this would be (2, 3).
        fractional_part (Tuple[int, ...]): A tuple representing the fractional
            places of the number. For 123;45, this would be (45,).

    Raises:
        InvalidFormatError: If the input string is not in a valid decimal or
            sexagesimal format, or if any sexagesimal part is >= 60.

    Examples:
        >>> a = Sexagesimal("04;10,30")
        >>> b = Sexagesimal(1.5)  # Creates Sexagesimal("01;30")
        >>> print(a + b)
        05;40,30
    """

    # The constructor
    def __init__(self, value: Union[str, int, float]):
        """
        Initialize a Sexagesimal instance from a variety of inputs.

        Summary:
            Construct an immutable sexagesimal (base-60) value from:

              - an existing Sexagesimal (copied),
              - a sexagesimal string like "01;30,15",
              - a decimal string like "1.5",
              - an int or float (treated as decimal).
            Decimal inputs are converted to sexagesimal; sexagesimal strings are
            parsed and validated; normalization (removal of extraneous zeros)
            is applied before the internal canonical representation is stored.

        Args:
            value (Union[str, int, float, Sexagesimal]):
                - Sexagesimal: instance to copy.
                - str: decimal ("1.5") or sexagesimal ("01;30,15" or "1;30").
                - int | float: treated as a decimal number and converted.

        Raises:
            InvalidFormatError: If the input string is not a valid decimal or
                sexagesimal format, or if parsing fails.
            InvalidFormatError: If any parsed sexagesimal digit is outside the
                valid range [0, BASE-1] (BASE == 60 in this module).

        Notes:
            - The constructor always stores a normalized, immutable SexagesimalParts
              container obtained via arithmetic.normalize_parts.
            - A Sexagesimal passed to the constructor is copied by reusing its
              internal parts object (no re-parsing).
            - Decimal-to-sexagesimal conversion uses the module conversion utilities
              with a reasonable default precision for fractional expansion.
        """
        # Step 0: Handle Sexagesimal input directly i.e Sexagesimal(Sexagesimal(...))
        if isinstance(value, Sexagesimal):
            self._parts = value._parts
            return

        # Step 1: Normalize input to string format for parsing
        str_value = str(value).strip()

        # Step 2: Extract the sign
        is_negative = False
        if str_value.startswith("-"):
            is_negative = True
            str_value = str_value[1:]

        # Step 3: Check if number is decimal, convert decimal strings to sexagesimal strings
        if PART_SEP not in str_value:
            str_value = conversion.from_decimal_str(str_value, 40)

        # Step 4: Parse the sexagesimal string into integer and fractional parts
        try:
            integer_str, fractional_str = str_value.split(PART_SEP)

            integer_parts = [int(part) for part in integer_str.split(VAL_SEP) if part]
            fractional_parts = [int(part) for part in fractional_str.split(VAL_SEP) if part]

        except (ValueError, IndexError):
            raise InvalidFormatError("Invalid input format. Expected decimal or sexagesimal string.")

        # Validate parts
        if any(part >= BASE for part in integer_parts):
            raise InvalidFormatError(f"Integer Part has a value greater than {BASE}")

        if any(part >= BASE for part in fractional_parts):
            raise InvalidFormatError(f"Fraction Part has a value greater than {BASE}")

        # Step 5: Normalize the parts (remove leading/trailing zeros) and create a frozen dataclass
        self._parts = arithmetic.normalize_parts(integer_parts, fractional_parts, is_negative)

    @classmethod
    def _from_parts(cls, parts: SexagesimalParts) -> "Sexagesimal":
        """
        Create a Sexagesimal instance directly from normalized parts.

        This internal classmethod constructs a new Sexagesimal object without invoking
        __init__, by attaching a pre-normalized SexagesimalParts container to the
        new instance. It is used throughout the implementation to return results
        produced by internal algorithms without re-parsing or re-normalizing.

        Args:
            parts (SexagesimalParts): An immutable, normalized parts container with:
                - is_negative (bool): sign of the value
                - integer_part (Tuple[int, ...]): canonical integer-place digits
                - fractional_part (Tuple[int, ...]): canonical fractional-place digits

        Returns:
            Sexagesimal: A new Sexagesimal instance whose internal _parts is `parts`.

        Notes:
            - The caller is responsible for ensuring `parts` are already normalized
              (no extraneous leading integer zeros or trailing fractional zeros,
              except the canonical zero representation).
            - This method preserves immutability by reusing the frozen SexagesimalParts.
        """
        instance: Sexagesimal = cls.__new__(cls)
        instance._parts = parts
        return instance

    # --- Public Properties for Safe, Read-Only Access ---
    @property
    def is_negative(self) -> bool:
        return self._parts.is_negative

    @property
    def integer_part(self) -> Tuple[int, ...]:
        return self._parts.integer_part

    @property
    def fractional_part(self) -> Tuple[int, ...]:
        return self._parts.fractional_part

    # The String representation of the class
    def __str__(self) -> str:
        """
        Return the canonical sexagesimal string representation.

        Produces a normalized string in the form "[sign]DD[,DD...];FF[,FF...]" where:
          - each degree or fractional place is zero-padded to two digits,
          - the integer and fractional parts are separated by ';',
          - individual places are separated by ','.
        Zero is always represented as "00;00" (no negative sign). Negative values are
        prefixed with a leading '-' character.

        Returns:
            str: Canonical sexagesimal string for this instance, e.g. "05;30,15" or "-01;00".
        """

        # Handle canonical zero representation
        if self._parts.integer_part == (0,) and self._parts.fractional_part == (0,):
            return "00;00"

        # Format integer part, ensuring at least one digit
        integer_str: str = (
            VAL_SEP.join(f"{part:02d}" for part in self._parts.integer_part) if self._parts.integer_part else "00"
        )

        # Format fractional part, ensuring at least one digit
        fractional_str: str = (
            VAL_SEP.join(f"{part:02d}" for part in self._parts.fractional_part) if self._parts.fractional_part else "00"
        )

        sign: str = "-" if self._parts.is_negative else ""

        return f"{sign}{integer_str}{PART_SEP}{fractional_str}"

    def __repr__(self) -> str:
        return f"Sexagesimal('{self!s}')"

    # The Addition of two Sexagesimal Numbers
    def __add__(self, other: "Sexagesimal") -> "Sexagesimal":
        if not isinstance(other, Sexagesimal):
            return NotImplemented

        # Handle Signs
        if self.is_negative and not other.is_negative:
            # i.e (-A) + B ==> B - A
            return other - (-self)
        elif not self.is_negative and other.is_negative:
            # i.e A + (-B) ==> A - B
            return self - (-other)

        # Now both are positive numbers or both are negative numbers
        normalized_parts = arithmetic.add(self._parts, other._parts)

        return Sexagesimal._from_parts(normalized_parts)

    # The Subtraction of two Sexagesimal Numbers
    def __sub__(self, other: "Sexagesimal") -> "Sexagesimal":
        if not isinstance(other, Sexagesimal):
            return NotImplemented

        # Handle signs
        if self.is_negative and not other.is_negative:
            # i.e (-A) - B ==> -(A + B)
            return -((-self) + other)

        elif not self.is_negative and other.is_negative:
            # i.e A - (-B) ==> A + B
            return self + (-other)

        elif self.is_negative and other.is_negative:
            # i.e (-A) - (-B) ==> B - A
            return (-other) - (-self)

        normalized_result_parts = arithmetic.subtract(self._parts, other._parts)

        return Sexagesimal._from_parts(normalized_result_parts)

    # The Multiplication of two Sexagesimal Numbers
    def __mul__(self, other: "Sexagesimal") -> "Sexagesimal":
        if not isinstance(other, Sexagesimal):
            return NotImplemented

        # Use the Multiplication Algorithm
        return Sexagesimal._from_parts(arithmetic.multiply_parts(self._parts, other._parts))

    # The Division of two Sexagesimal Numbers
    def __truediv__(self, other: "Sexagesimal") -> "Sexagesimal":
        if not isinstance(other, Sexagesimal):
            return NotImplemented

        # Step 1: Handle division by zero
        if other == Sexagesimal(0):
            raise ZeroDivisionError("Division by zero is not allowed.")

        # Step 2: Convert both numbers to Rational
        self_rational: Rational = conversion.to_rational(self)
        other_rational: Rational = conversion.to_rational(other)

        # Step 3: Perform division in Rational
        result_rational: Rational = self_rational / other_rational  # type: ignore

        # Step 4: Convert the result back to (normalized) Sexagesimal parts
        result_parts: SexagesimalParts = conversion.rational_to_sexagesimal_parts(result_rational)

        return Sexagesimal._from_parts(result_parts)

    # Negation (For Unary Minus)
    def __neg__(self) -> "Sexagesimal":
        if self == Sexagesimal(0):
            return self

        return Sexagesimal._from_parts(
            SexagesimalParts(
                is_negative=not self._parts.is_negative,
                integer_part=self._parts.integer_part,
                fractional_part=self._parts.fractional_part,
            )
        )

    # For Unary Plus
    def __pos__(self) -> "Sexagesimal":
        # Again, don't return the original number
        return self

    # Absolute Value
    def __abs__(self) -> "Sexagesimal":
        return Sexagesimal._from_parts(
            SexagesimalParts(
                is_negative=False,
                integer_part=self._parts.integer_part,
                fractional_part=self._parts.fractional_part,
            )
        )

    # The Power of a Sexagesimal Number
    def __pow__(self, n: int) -> "Sexagesimal":
        """
        __pow__ Calculates the power of a Sexagesimal number to an integer n.

        This method supports positive, negative, and zero integer n,
        leveraging the existing multiplication and division methods of the class.

        - For positive n, it uses repeated multiplication.
        - For a zero n, it returns 1 (Sexagesimal('01;00')).
        - For negative n, it calculates the reciprocal of the positive power.

        Args:
            n (int): The integer n to raise the number to.

        Returns:
            Sexagesimal: The result of the power operation.

        Raises:
            TypeError: If the n is not an integer.
            ZeroDivisionError: If the base is zero and the n is negative.
        """

        if not isinstance(n, int):
            raise TypeError("Exponent must be an integer.")

        if n == 0:
            return Sexagesimal(1)  # Any number to the power of 0 is 1

        if n < 0:
            if self == Sexagesimal(0):
                raise ZeroDivisionError("0 cannot be raised to a negative power.")

            return Sexagesimal(1) / (self**-n)

        # Start with the identity element for multiplication
        result = Sexagesimal(1)
        base = self

        while n > 0:
            if n % 2 == 1:
                result *= base
            base *= base
            n //= 2

        return result

    # Iterative Addition
    def __iadd__(self, other: "Sexagesimal") -> "Sexagesimal":
        # Use the Addition Algorithm
        return self + other

    # Iterative Subtraction
    def __isub__(self, other: "Sexagesimal") -> "Sexagesimal":
        # Use the Subtraction Algorithm
        return self - other

    # Iterative Multiplication
    def __imul__(self, other: "Sexagesimal") -> "Sexagesimal":
        # Use the Multiplication Algorithm
        return self * other

    # Greater Than
    def __gt__(self, other: "Sexagesimal") -> bool:
        if not isinstance(other, Sexagesimal):
            return NotImplemented

        if not self.is_negative and other.is_negative:
            return True

        if self.is_negative and not other.is_negative:
            return False

        if self.is_negative and other.is_negative:
            return -self < -other  # <==> self > other

        # Now both are positive numbers
        comparison: int = arithmetic.compare_magnitude(self._parts, other._parts)
        return comparison > 0

    # Less Than
    def __lt__(self, other: "Sexagesimal") -> bool:
        if not isinstance(other, Sexagesimal):
            return NotImplemented

        if not self.is_negative and other.is_negative:
            return False

        if self.is_negative and not other.is_negative:
            return True

        if self.is_negative and other.is_negative:
            return -self > -other  # <==> self > other

        # Now both are positive numbers
        comparison: int = arithmetic.compare_magnitude(self._parts, other._parts)
        return comparison < 0

    # Equal To
    def __eq__(self, other: object) -> bool:
        # Ensure other is a Sexagesimal instance before comparing
        if not isinstance(other, Sexagesimal):
            return NotImplemented

        return self._parts == other._parts

    # Not Equal To
    def __ne__(self, other: object) -> bool:
        # Ensure other is a Sexagesimal instance before comparing
        if not isinstance(other, Sexagesimal):
            return NotImplemented

        return not self == other

    # Greater Than or Equal To
    def __ge__(self, other: "Sexagesimal") -> bool:
        return self > other or self == other

    # Less Than or Equal To
    def __le__(self, other: "Sexagesimal") -> bool:
        return self < other or self == other

    def to_decimal(self, precision: int = 50) -> Decimal:
        """
        Convert the Sexagesimal number to a high-precision Decimal.

        Summary:
            Produce a Decimal representation of this sexagesimal value by
            summing integer-place digits weighted by BASE**k (k = 0,1,2,...)
            and fractional-place digits as digit/BASE**k (k = 1,2,...). The
            global Decimal context precision is set to `precision` for the
            duration of the computation.

        Args:
            precision (int, optional): Number of significant digits to use in
                the Decimal context (localcontext().prec). Must be a positive
                integer. Defaults to 50.

        Returns:
            Decimal: A Decimal equal to the numeric value of this Sexagesimal.
                The returned Decimal carries the same sign as the instance;
                canonical zero is returned as a non-negative Decimal.

        Notes:
            - This function mutates the module Decimal context via localcontext().prec.
              Callers that rely on a different global Decimal precision should
              restore it after calling this method if necessary.
            - All accumulation uses Decimal arithmetic to avoid floating-point
              rounding; the result is as exact as allowed by the requested precision.
        """

        # Set the precision for Decimal operations
        with localcontext() as ctx:
            ctx.prec = precision

            total = Decimal(0)

            # Sum of integer digits
            for idx, digit in enumerate(reversed(self.integer_part)):
                total += Decimal(digit) * (Decimal(BASE) ** idx)

            # Sum of fractional digits
            for idx, digit in enumerate(self.fractional_part, start=1):
                total += Decimal(digit) / (Decimal(BASE) ** idx)

            return -total if self.is_negative else total

    # Round off the given Sexagesimal Number to the given precision
    def round(self, precision: int = 0) -> "Sexagesimal":
        """
        Round the sexagesimal number to the specified fractional-place precision.

        Summary:
            Truncate the fractional part to `precision` base-60 places and perform
            round-half-up based on the next (precision-th) fractional digit
            (round up when that digit >= BASE//2). Carries produced by rounding
            propagate through fractional places into the integer places as needed,
            and the final result is normalized. Zero is canonicalized as
            non-negative.

        Args:
            precision (int, optional): Number of fractional base-60 places to keep.
                0 means rounding to the integer part. Must be a non-negative integer.
                Defaults to 0.

        Raises:
            TypeError: If `precision` is not an int.
            ValueError: If `precision` is negative.

        Returns:
            Sexagesimal: A new Sexagesimal instance rounded to the requested precision.

        Notes:
            - If `precision` is greater than or equal to the current fractional
              length, the original instance is returned (no change).
            - Carry propagation may extend the integer part (creating a new high-order
              digit) and normalization removes any extraneous zeros.
        """

        if not isinstance(precision, int):
            raise TypeError("Precision must be an integer.")

        if precision < 0:
            raise ValueError("Precision must be a non-negative integer.")

        if precision >= len(self.fractional_part):
            return self  # No rounding needed

        # Determine if we need to round up
        round_up: bool = self.fractional_part[precision] >= (BASE // 2)

        # Truncate the fractional part
        new_frac_list: list[int] = list(self.fractional_part[:precision])

        if not round_up:
            # No rounding up needed
            new_parts = arithmetic.normalize_parts(list(self.integer_part), new_frac_list, self.is_negative)
            return Sexagesimal._from_parts(new_parts)

        # ------------------------- Handling the rounding up ------------------------- #
        if not new_frac_list:  # Rounding to integer part
            carry = 1
        else:
            new_frac_list[-1] += 1
            carry = 0

        # Propagate carry in fractional part
        for idx, val in reversed(list(enumerate(new_frac_list))):
            val += carry
            if val >= BASE:
                new_frac_list[idx] = val % BASE
                carry = val // BASE
            else:
                new_frac_list[idx] = val
                carry = 0
                break

        # If there's still a carry, propagate it to the integer part
        new_int_list = list(self.integer_part)

        if carry > 0:
            new_int_list[-1] += carry
            for idx in range(len(new_int_list) - 1, -1, -1):
                if new_int_list[idx] < BASE:
                    carry = 0
                    break

                carry = new_int_list[idx] // BASE
                new_int_list[idx] = new_int_list[idx] % BASE

                if idx > 0:
                    new_int_list[idx - 1] += carry
                else:
                    new_int_list.insert(0, carry)

        new_parts = arithmetic.normalize_parts(new_int_list, new_frac_list, self.is_negative)
        return Sexagesimal._from_parts(new_parts)
