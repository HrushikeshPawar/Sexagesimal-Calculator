# Imports
from typing import Tuple, Union
from decimal import Decimal, getcontext

from sympy import Rational

from sexagesimal_calculator import conversion
from sexagesimal_calculator import arithmetic

from sexagesimal_calculator.core import BASE, PART_SEP, VAL_SEP, _SexagesimalParts
from sexagesimal_calculator.utils import _normalize_parts
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
        ValueError: If the input string is not in a valid decimal or
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
        Initialize a Sexagesimal instance.

        Create an immutable sexagesimal (base-60) number from a string, int, float, or another Sexagesimal.
        Decimal inputs (e.g. 1.5 or "1.5") are converted to sexagesimal; sexagesimal strings (e.g. "01;30,15")
        are validated and normalized; passing a Sexagesimal returns an equivalent instance.

        Args:
            value (Union[str, int, float, Sexagesimal]): The value to initialize the instance from.
                - str: a decimal string ("1.5") or a sexagesimal string ("01;30,15" or "1;30").
                - int or float: treated as a decimal number and converted to sexagesimal.
                - Sexagesimal: an existing instance whose internal parts are copied.

        Raises:
            ValueError: If the input cannot be parsed as a decimal or sexagesimal string.
            ValueError: If any sexagesimal part is not in the valid range [0, 59].

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
        self._parts = _normalize_parts(integer_parts, fractional_parts, is_negative)

    @classmethod
    def _from_parts(cls, parts: _SexagesimalParts) -> "Sexagesimal":
        """
        Create a Sexagesimal instance directly from normalized parts.

        This internal classmethod constructs a new Sexagesimal object without invoking
        __init__, by attaching a pre-normalized _SexagesimalParts container to the
        new instance. It is used throughout the implementation to return results
        produced by internal algorithms without re-parsing or re-normalizing.

        Args:
            parts (_SexagesimalParts): An immutable, normalized parts container with:
                - is_negative (bool): sign of the value
                - integer_part (Tuple[int, ...]): canonical integer-place digits
                - fractional_part (Tuple[int, ...]): canonical fractional-place digits

        Returns:
            Sexagesimal: A new Sexagesimal instance whose internal _parts is `parts`.

        Notes:
            - The caller is responsible for ensuring `parts` are already normalized
              (no extraneous leading integer zeros or trailing fractional zeros,
              except the canonical zero representation).
            - This method preserves immutability by reusing the frozen _SexagesimalParts.
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
        return Sexagesimal._from_parts(arithmetic._multiply_parts(self._parts, other._parts))

    # The Division of two Sexagesimal Numbers
    def __truediv__(self, other: "Sexagesimal") -> "Sexagesimal":
        if not isinstance(other, Sexagesimal):
            return NotImplemented

        # Step 1: Handle division by zero
        if other == Sexagesimal(0):
            raise ZeroDivisionError("Division by zero is not allowed.")

        # Step 2: Convert both numbers to Rational
        self_rational: Rational = conversion._to_rational(self)
        other_rational: Rational = conversion._to_rational(other)

        # Step 3: Perform division in Rational
        result_rational: Rational = self_rational / other_rational  # type: ignore

        # Step 4: Convert the result back to (normalized) Sexagesimal parts
        result_parts: _SexagesimalParts = conversion._rational_to_sexagesimal_parts(result_rational)

        return Sexagesimal._from_parts(result_parts)

    # Negation (For Unary Minus)
    def __neg__(self) -> "Sexagesimal":
        if self == Sexagesimal(0):
            return self

        return Sexagesimal._from_parts(
            _SexagesimalParts(
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
            _SexagesimalParts(
                is_negative=False,
                integer_part=self._parts.integer_part,
                fractional_part=self._parts.fractional_part,
            )
        )

    # The Power of a Sexagesimal Number
    def __pow__(self, n: int) -> "Sexagesimal":
        """
        __pow__ Calculates the power of a Sexagesimal number to an integer exponent.

        This method supports positive, negative, and zero integer exponents,
        leveraging the existing multiplication and division methods of the class.

        - For positive exponents, it uses repeated multiplication.
        - For a zero exponent, it returns 1 (Sexagesimal('01;00')).
        - For negative exponents, it calculates the reciprocal of the positive power.

        Args:
            exponent (int): The integer exponent to raise the number to.

        Returns:
            Sexagesimal: The result of the power operation.

        Raises:
            TypeError: If the exponent is not an integer.
            ZeroDivisionError: If the base is zero and the exponent is negative.
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
        comparison: int = arithmetic._compare_magnitude(self._parts, other._parts)
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
        comparison: int = arithmetic._compare_magnitude(self._parts, other._parts)
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
                the Decimal context (getcontext().prec). Must be a positive
                integer. Defaults to 50.

        Returns:
            Decimal: A Decimal equal to the numeric value of this Sexagesimal.
                The returned Decimal carries the same sign as the instance;
                canonical zero is returned as a non-negative Decimal.

        Notes:
            - This function mutates the module Decimal context via getcontext().prec.
              Callers that rely on a different global Decimal precision should
              restore it after calling this method if necessary.
            - All accumulation uses Decimal arithmetic to avoid floating-point
              rounding; the result is as exact as allowed by the requested precision.
        """

        # Set the precision for Decimal operations
        getcontext().prec = precision

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
            new_parts = _normalize_parts(list(self.integer_part), new_frac_list, self.is_negative)
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

        new_parts = _normalize_parts(new_int_list, new_frac_list, self.is_negative)
        return Sexagesimal._from_parts(new_parts)

    # Convert the given Sexagesimal Number from Mod 60 (default form) to Mod N. Output is a string
    @staticmethod
    def mod60ToMod(Input: "Sexagesimal", mod: int) -> str:
        try:
            A = Input.S
        except AttributeError:  # if Input is not a Sexagesimal Object
            print("Not a Sexagesimal Object")
            return

        A_D, A_F = A.split(";")
        A_D = A_D.split(",")

        New_A_D = []
        for i in range(len(A_D)):
            elem = A_D[-(i + 1)]
            New_A_D.append(int(elem) * (60**i))

        N = sum(New_A_D)
        D = N % mod

        return f"{D};{A_F}"

    # Multipling the two sexagesimal numbers
    @staticmethod
    def Multiplication(
        A: Union["Sexagesimal", str],
        B: Union["Sexagesimal", str],
        verbose: bool = False,
    ):
        # Get A and B as right form of Sexagesimal string
        try:
            A_S = A.S
            B_S = B.S
        except AttributeError:  # If Input is just a string
            A = Sexagesimal(A)
            B = Sexagesimal(B)
            A_S = A.S
            B_S = B.S

        # Break down both numbers in their Integral and Fractional Part
        A_D, A_F = A_S.split(";")
        A_D = A_D.split(",")
        A_F = A_F.split(",")
        B_D, B_F = B_S.split(";")
        B_D = B_D.split(",")
        B_F = B_F.split(",")

        # Print the above details
        Details = "\n\n\n\n**Inputs:**"
        Details += f"\n\n\tA\t=\t{A}"
        Details += f"\n\tB\t=\t{B}"

        Details += (
            "\n\n\n\n**Step 1:** Break the Sexagesimal Numbers in their Intergral and Fractional Parts respectively."
        )
        Details += f"\n\n\tIntegral part of A\t\t=\t{A_D}"
        Details += f"\n\tFractional part of A\t=\t{A_F}"
        Details += f"\n\n\tIntegral part of B\t\t=\t{B_D}"
        Details += f"\n\tFractional part of B\t=\t{B_F}"

        # A List to store all the intermediate Multiplication Results
        Multiplication = []

        # Multiply the Fractional part of B with A:
        Details += "\n\n\n\n**Step 2:** Multiply the fractional part of B to A, one Sexagesimal place at a time.\n"
        for f in B_F[::-1]:
            carry = 0
            f = int(f)
            i = len(Multiplication)

            if i == 0:
                Multiplication.append([])
            else:
                Multiplication.append([0 for _ in range(i)])

            for A_f in A_F[::-1]:
                carry_old = carry
                A_f = int(A_f)
                prod = f * A_f + carry

                if prod > 59:
                    carry = prod // 60
                    prod %= 60
                else:
                    carry = 0

                Multiplication[i] = [prod] + Multiplication[i]
                Details += f"\n\t{f:0>2}  *  {A_f:0>2}  +  {carry_old:0>2}\t=\t{60 * carry + prod:0>2}\t=\t60 * {carry:0>2} + {prod:0>2}"

            for A_d in A_D[::-1]:
                carry_old = carry
                A_d = int(A_d)
                prod = f * A_d + carry

                if prod > 59:
                    carry = prod // 60
                    prod %= 60
                else:
                    carry = 0

                Multiplication[i] = [prod] + Multiplication[i]
                Details += f"\n\t{f:0>2}  *  {A_d:0>2}  +  {carry_old:0>2}\t=\t{60 * carry + prod:0>2}\t=\t60 * {carry:0>2} + {prod:0>2}"

            if carry > 0:
                while carry > 59:
                    R = carry % 60
                    carry = carry // 60
                    Multiplication[i] = [R] + Multiplication[i]
                Multiplication[i] = [carry] + Multiplication[i]

            Details += f"\n\n\t{f}  *  {A}\t=\t{Multiplication[i]}\n"

        # Multiply the Integral part of B with A:
        Details += "\n\n\n\n**Step 3:** Multiply the integral part of B to A, one Sexagesimal place at a time.\n"
        for d in B_D[::-1]:
            d = int(d)
            carry = 0
            i = len(Multiplication)

            if i == 0:
                Multiplication.append([])
            else:
                Multiplication.append(i * [0])

            for A_f in A_F[::-1]:
                carry_old = carry
                A_f = int(A_f)
                prod = d * A_f + carry

                if prod > 59:
                    carry = prod // 60
                    prod %= 60
                else:
                    carry = 0

                Multiplication[i] = [prod] + Multiplication[i]
                Details += f"\n\t{d:0>2}  *  {A_f:0>2}  +  {carry_old:0>2}\t=\t{60 * carry + prod:0>2}\t=\t60 * {carry:0>2} + {prod:0>2}"

            for A_d in A_D[::-1]:
                carry_old = carry
                A_d = int(A_d)
                prod = d * A_d + carry

                if prod > 59:
                    carry = prod // 60
                    prod %= 60
                else:
                    carry = 0

                Multiplication[i] = [prod] + Multiplication[i]
                Details += f"\n\t{d:0>2}  *  {A_d:0>2}  +  {carry_old:0>2}\t=\t{60 * carry + prod:0>2}\t=\t60 * {carry:0>2} + {prod:0>2}"

            if carry > 0:
                while carry > 59:
                    R = carry % 60
                    carry = carry // 60
                    Multiplication[i] = [R] + Multiplication[i]
                Multiplication[i] = [carry] + Multiplication[i]

            Details += f"\n\n\t{d}  *  {A}\t=\t{Multiplication[i]}\n"

        # Step 4: Make all the rows of equal length
        Details += "\n\n\n\n**Step 4:** Make all the rows of equal lenght to get the following matrix of all the intermediate results\n"
        max_lenght = max([len(x) for x in Multiplication])
        for i in range(len(Multiplication)):
            m = max_lenght - len(Multiplication[i])

            Multiplication[i] = m * [0] + Multiplication[i]

        for row in Multiplication:
            Row = []
            for elem in row:
                Row.append(f"{elem:0>2}")

            Row = " | ".join(Row)
            Details += f"\n\t | {Row} |"

        # Step 5: Add all the rows, column by column, from right to left
        Details += "\n\n\n\n**Step 5:** Add all the rows, column by column, from right to left. Following is the final result of addition\n"
        Result = []
        carry = 0
        for i in list(range(len(Multiplication[0])))[::-1]:
            elems = []
            for j in range(len(Multiplication)):
                elems.append(Multiplication[j][i])
            Sum = sum(elems) + carry

            if Sum > 59:
                carry = Sum // 60
                Sum %= 60
            else:
                carry = 0

            Result = [f"{Sum:0>2}"] + Result

        if carry > 0:
            while carry > 59:
                R = carry % 60
                carry = carry // 60
                Result = [f"{R:0>2}"] + Result
            Result = [f"{carry:0>2}"] + Result

        for row in Multiplication:
            Row = []
            i = len(Result) - len(row)
            row = ["00"] * i + row
            for elem in row:
                Row.append(f"{elem:0>2}")
            Row = " | ".join(Row)
            Details += f"\n\t | {Row} | "

        Details += f"\n\t{'=' * (len(Row) + 6)}"
        Row = []
        for elem in Result:
            Row.append(f"{elem:0>2}")
        Row = " | ".join(Row)
        Details += f"\n\t | {Row} | "

        # Step 6: Divide the result into the Integral and the Fractional Part (Using the length of A_F and B_F)
        Details += "\n\n\n\n**Step 6:** Divide the result into the Integral and the Fractional Part (Using the length of A_F and B_F)\n"

        k = len(A_F) + len(B_F)
        D, F = Result[:-k], Result[-k:]
        D = ",".join(D)
        F = ",".join(F)
        Details += f"\n     Result  =  {D};{F}"

        # Step 7: Strip the trailing or preceeding zeros from the result, if any
        Details += "\n\n\n\n**Step 7:** Strip the trailing or preceeding zeros from the result, if any"
        while F[-3:] == ",00":
            F = F[:-3]

        while D[:3] == "00,":
            D = D[3:]

        Details += f"\n\n       Result  =  {D};{F}"

        # Step 8: Give proper sign to the Result
        Details += "\n\n\n\n**Step 8:** Give proper sign to the Result"
        if (A.negative is True and B.negative is False) or (A.negative is False and B.negative is True):
            Details += f"\n\n\t{A}  *  {B}  =  -{D};{F}\n\n"
            # return (Sexagesimal(f"-{D};{F}"), Details)
            result = Sexagesimal(f"-{D};{F}")
        else:
            Details += f"\n\n\t{A}  *  {B}  =  {D};{F}\n\n"
            # return (Sexagesimal(f"{D};{F}"), Details)
            result = Sexagesimal(f"{D};{F}")

        if verbose:
            return (result, Details)
        else:
            return result

    # Division of two Sexagesimal Numbers
    @staticmethod
    def Division(
        A: Union["Sexagesimal", str],
        B: Union["Sexagesimal", str],
        precision: int = 20,
        verbose: bool = False,
    ):
        # Get A and B as right form of Sexagesimal string
        try:
            A.S
            B.S
        except AttributeError:  # If A or B is not a Sexagesimal object
            A = Sexagesimal(A)
            B = Sexagesimal(B)

        # Print the above details
        Details = "\n\n\n\n**Inputs:**"
        Details += f"\n\n\tA\t=\t{A}"
        Details += f"\n\tB\t=\t{B}"

        # Step1 : Get the Rational Form of B
        try:
            B_Num, B_Denom = str(Sexagesimal.getRationlForm(B)).split("/")
        except ValueError:  # Not enough values to unpack
            B_Num = str(Sexagesimal.getRationlForm(B))
            B_Denom = 1

        Details += "\n\n\nStep 1: Get the rational form of B"
        Details += f"\n\tB\t=\t {B_Num}"
        Details += f"\t \t \t{'-' * (len(B_Num) + 2)}"
        Details += f"\t \t \t {B_Denom}"

        # Step 2: Get Reciprocal of the B_Num
        B_Num_R, Recur, flag = Sexagesimal.getReciprocal(int(B_Num), precision + 10)
        B_Num_R1 = Sexagesimal(B_Num_R)

        Details += "\n\n\nStep 2: Get the reciprocal of the numberator of B (Why? Because, dividing by B is same as multiplying by reciprocal of B)"
        if flag:
            Details += "\n\tThe numerator of B is not a regular number (i.e has a prime factor other than 2, 3 or 5)."
            Details += "\tHence, the reciprocal of numberator is non-terminating but recurring! (The recurring term is enclosed on brackets)"
        else:
            Details += "\n\tThe numerator of B is a regular number. Hence, the reciprocal has an exact Sexagesimal Representation"

        if len(Recur) == 0:
            if len(B_Num_R.split(";")[1].split(",")) > precision:
                B_Num_R = Sexagesimal.RoundOff(B_Num_R, precision)

            Details += f"\n\tReciprocal of numerator {B_Num}\t=\t{B_Num_R}"
        else:
            Details += f"\n\tReciprocal of numerator {B_Num}\t=\t{Recur}"

        # Step 3: Now we get the Reciprocal of B
        B_Denom = Sexagesimal(B_Denom)
        B_R = B_Num_R1 * B_Denom

        Details += "\n\n\nStep 3: Calculate the Reciprocal of B (Denominator x Reciprocal of Numerator)"
        Details += f"\n\tReciprocal of B (B')\t=\t{B_R}"

        # Step 4: And now we do the actual divison. Which is nothing but multiplication with the reciprocal
        Div = A * B_R
        if A.negative and B.negative is False:
            Div.negative = True
        elif A.negative is False and B.negative:
            Div.negative = True
        else:
            Div.negative = False

        if len(Div.split(";")[1].split(",")) > precision:
            Div = Sexagesimal.RoundOff(Div, precision)

        Details += "\n\n\nStpe 4: Do the actual Division (A/B = A * B')"
        Details += f"\n\tA/B\t=\t{Div}"

        if flag:
            A_D, A_F = A.split(";")
            A_D = A_D.split(",")
            A_F = A_F.split(",")

            A_New = Div * B
            A_New_D, A_New_F = A_New.split(";")
            A_New_D = A_New_D.split(",")
            A_New_F = A_New_F.split(",")

            cnt = 0
            for i in range(len(A_F)):
                if A_F[i] != A_New_F[i]:
                    break
                else:
                    cnt += 1

            Details += f"\n\nThe above answer of division (A/B) when again multiplied with B gives A correctly upto {cnt} Sexagesimal places in the fraction part\n"
            Details += f"\n\tA'\t=\tA/B * B\t=\t{A_New}\n\n"

        if verbose:
            return (Div, Details)
        else:
            return Div

    @staticmethod
    def IncrementTableGenerator(Inc_Initial, Inc_Increment, Inc_Rows=10, Inc_Mod=60):
        Inc_Initial = Sexagesimal(Inc_Initial)
        Inc_Increment = Sexagesimal(Inc_Increment)

        if Inc_Mod < 2:
            Inc_Mod = 0

        A = Sexagesimal(Inc_Initial)
        i = 0
        Inc_output = []

        if A.negative:
            Inc_output.append(f"-{A.S}")
        else:
            Inc_output.append(A.S)

        while i < Inc_Rows:
            B = Sexagesimal(Inc_Increment)
            A = A + B

            A_I = Sexagesimal.Integral2Decimal(A)
            A_D, A_F = A_I.split(";")

            if Inc_Mod == 0:
                if A.negative is True and A.S != "00;00":
                    A = Sexagesimal(f"-{A_D};{A_F}")
                    Inc_output.appned(f"-{Sexagesimal.Integral2Decimal(A)}")

                else:
                    A = Sexagesimal(f"{A_D};{A_F}")
                    Inc_output.append(f"{Sexagesimal.Integral2Decimal(A)}")

            else:
                A_D = int(A_D) % Inc_Mod

                if A.negative is True and A.S != "00;00":
                    A = Sexagesimal(f"-{A_D};{A_F}")
                    if Inc_Mod > 60:
                        Inc_output.append(f"-{Sexagesimal.Integral2Decimal(A)}")
                    else:
                        Inc_output.append(f"-{A.S}")
                else:
                    A = Sexagesimal(f"{A_D};{A_F}")
                    if Inc_Mod > 60:
                        Inc_output.append(f"{Sexagesimal.Integral2Decimal(A)}")
                    else:
                        Inc_output.append(f"{A.S}")
            i += 1

        return Inc_output

    @staticmethod
    def IntegralModN(A, N):
        A = Sexagesimal(A)
        A_D, A_F = A.split(";")
        A_D = A_D.split(",")[::-1]

        D = 0
        for i, d in enumerate(A_D):
            D += int(d) * (60**i)

        M = int(D)
        D = []
        while M > N - 1:
            R = M % N
            M = M // N
            D = [f"{R:0>2}"] + D
        D = [f"{M:0>2}"] + D

        A_D = ",".join(D)
        return Sexagesimal(f"{A_D};{A_F}")
