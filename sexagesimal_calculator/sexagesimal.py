# Imports
from decimal import Decimal, getcontext, InvalidOperation
from sympy import Rational
from math import pow
from copy import copy
from typing import Union, List, Tuple


# The Sexagesimal class
class Sexagesimal:

    # The constructor
    def __init__(self, S: Union[str, int]):

        # Get the input as String
        S = str(S).strip()

        # Perform negative number check
        S = self.process_negative(S)

        # If number is decimal, convert to sexagesimal
        S = self.check_and_convert_decimal(S)

        # At this point, the input is in sexagesimal format, hence we
        # Finally Check if the input is valid Sexagesimal
        is_valid, error = self.is_valid_sexagesimal(S)

        # If not valid, raise the error
        if not is_valid:
            raise error

        # If valid, Convert the String to Standard Sexagesimal Format
        self.S = self.Standardize(S)

    # The String representation of the class
    def __str__(self) -> str:

        if self.S == Sexagesimal(0).S:
            self.negative = False

        # Get the string
        S = self.S

        # Add the negative sign if negative
        if self.negative:
            S = "-" + S

        return S

    # The Addition of two Sexagesimal Numbers
    def __add__(self, B: "Sexagesimal") -> "Sexagesimal":

        # Get the terms (Don't want to accidentally change the original numbers)
        A = copy(self)
        B = copy(B)

        # Make them equal lengths, i.e in terms of Degrees and Fractional part
        A1, B1 = self.makeEqualLen(A, B)

        # Separate the Integer and the fraction part
        A_D, A_F = A1.split(";")
        B_D, B_F = B1.split(";")

        # Convert String to List
        A_D = self.input2List(A_D)
        A_F = self.input2List(A_F)
        B_D = self.input2List(B_D)
        B_F = self.input2List(B_F)

        # If one of the numbers is negative and other is positive
        # Then it is same as  subtracting two positive numbers (order depends on the sign)
        if A.negative and not B.negative:
            # Make A positive
            return B - (-A)

        elif not A.negative and B.negative:
            # Make B positive
            return A - (-B)

        # If both are negative or both are positive, then we add them
        # And give the result the same sign as the numbers
        # First Add the fractional part
        # We use the most basic algorithm for addition of two numbers
        # The one we learned in school (add with carry)
        F = []  # To Store the result of fractional part addition
        carry = 0  # To store the carry

        # Loop until we cover all the fractional digits
        while len(A_F) > 0:

            # Get the (current) last digits of both numbers
            a, b = A_F.pop(), B_F.pop()

            # Add them with the carry
            Sum = a + b + carry

            # If the sum is greater than 60, then we have a carry
            # While Initializing the Sexagesimal class, we made sure that fractional part has digits always less than 60
            # Hence be sure that in any case, the sum will be less than 120
            if Sum >= 60:
                Sum -= 60
                carry = 1
            else:
                carry = 0

            F = [f"{Sum:0>2}"] + F

        # Same for the degrees part
        D = []

        # Loop until we cover all the degree digits
        while len(A_D) > 0:

            # Get the (current) last digits of both numbers
            a, b = A_D.pop(), B_D.pop()

            # Add them with the carry
            Sum = a + b + carry

            # If the sum is greater than 60, then we have a carry
            if Sum >= 60:
                Sum -= 60
                carry = 1
            else:
                carry = 0

            D = [f"{Sum:0>2}"] + D

        # Join the lists to get the final result
        D = ",".join(D)
        F = ",".join(F)
        S = ";".join([D, F])

        # Finally decide the sign of the result
        if A.negative and B.negative:
            S = "-" + S

        return Sexagesimal(S)

    # The Subtraction of two Sexagesimal Numbers
    def __sub__(self, B: "Sexagesimal") -> "Sexagesimal":

        # Get the terms (Don't want to accidentally change the original numbers)
        A = copy(self)
        B = copy(B)

        # If one of the numbers is negative and other is positive
        # Then it is same as adding two positive numbers (with answer having the sign of the bigger number)
        if (A.negative and not B.negative) or (B.negative and not A.negative):
            return A + (-B)

        # If both are positive, then we subtract them as positive numbers
        # And give the result the same sign as the numbers
        # Start with the fractional part
        # We use the most basic algorithm for subtraction of two numbers
        # Subtract the smaller number from the bigger number
        if not A.negative and not B.negative:

            # Make them equal lengths
            A1, B1 = self.makeEqualLen(A, B)

            # Separate the Integer and the fraction part
            A_D, A_F = A1.split(";")
            B_D, B_F = B1.split(";")

            # Convert String to List
            A_D = self.input2List(A_D)
            A_F = self.input2List(A_F)
            B_D = self.input2List(B_D)
            B_F = self.input2List(B_F)

            if A > B:
                return self.subtraction_with_borrow(A_D, A_F, B_D, B_F)
            else:
                return self.subtraction_with_borrow(B_D, B_F, A_D, A_F)

        # Finally if nothing of the above, then both are negative
        # Then it same as addition of two numbers we negative sign to the result
        return A + (-B)

    # The Multiplication of two Sexagesimal Numbers
    def __mul__(self, B: "Sexagesimal") -> "Sexagesimal":

        # Use the Multiplication Algorithm with default parameters
        return self.Multiplication(self, B)

    # The Division of two Sexagesimal Numbers
    def __truediv__(self, B: "Sexagesimal") -> "Sexagesimal":

        # Use the Division Algorithm with default parameters
        return self.Division(self, B)

    # Negation (For Unary Minus)
    def __neg__(self) -> "Sexagesimal":

        # Don't accidentally change the original number
        A = copy(self)
        A.negative = not A.negative

        return A

    # For Unary Plus
    def __pos__(self) -> "Sexagesimal":
        # Again, don't return the original number
        return copy(self)

    # Absolute Value
    def __abs__(self) -> "Sexagesimal":

        # Don't return the original number
        A = copy(self)

        # Set the negative flag to False
        A.negative = False

        return A

    # The Power of a Sexagesimal Number
    def __pow__(self, n: int) -> "Sexagesimal":

        # Don't return the original number
        A = copy(self)

        # If the power is negative, then we raise the reciprocal to the power
        if n < 0:
            A = 1 / A
            n = -n

        # Perform repeated multiplication
        for _ in range(n - 1):
            A *= A

        return A

    # Iterative Addition
    def __iadd__(self, B: "Sexagesimal") -> "Sexagesimal":

        # Use the Addition Algorithm
        return self + B

    # Iterative Subtraction
    def __isub__(self, B: "Sexagesimal") -> "Sexagesimal":

        # Use the Subtraction Algorithm
        return self - B

    # Iterative Multiplication
    def __imul__(self, B: "Sexagesimal") -> "Sexagesimal":
        # Use the Multiplication Algorithm
        return self * B

    # Greater Than
    def __gt__(self, B: "Sexagesimal") -> bool:

        # Get the terms (Don't want to accidentally change the original numbers)
        A = copy(self)
        B = copy(B)

        # If one of the numbers is negative and other is greater
        if A.negative and not B.negative:
            return False

        if not A.negative and B.negative:
            return True

        if A.negative and B.negative:
            return -A < -B  # <==> A > B

        # Make them equal lengths
        A, B = self.makeEqualLen(A, B)
        A_D, A_F = A.split(";")
        B_D, B_F = B.split(";")

        for i in range(len(A_D)):
            if A_D[i] > B_D[i]:
                return True

            if B_D[i] > A_D[i]:
                return False

        for i in range(len(A_F)):
            if A_F[i] > B_F[i]:
                return True

            if B_F[i] > A_F[i]:
                return False

        # If equal then return False
        return False

    # Less Than
    def __lt__(self, B: "Sexagesimal") -> bool:

        # Get the terms (Don't want to accidentally change the original numbers)
        A = copy(self)
        B = copy(B)

        # If one of the numbers is negative and other is greater
        if A.negative and not B.negative:
            return True

        if not A.negative and B.negative:
            return False

        if A.negative and B.negative:
            return -A > -B  # <==> A < B

        # Make them equal lengths
        A, B = self.makeEqualLen(A, B)

        A_D, A_F = A.split(";")
        B_D, B_F = B.split(";")

        for i in range(len(A_D)):
            if A_D[i] < B_D[i]:
                return True

            if B_D[i] < A_D[i]:
                return False

        for i in range(len(A_F)):
            if A_F[i] < B_F[i]:
                return True

            if B_F[i] < A_F[i]:
                return False

        # If equal then return False
        return False

    # Equal To
    def __eq__(self, B: "Sexagesimal") -> bool:

        # return not (self < B or self > B)
        return (self.negative == B.negative) and (self.S == B.S)

    # Not Equal To
    def __ne__(self, B: "Sexagesimal") -> bool:
        return not self == B

    # Greater Than or Equal To
    def __ge__(self, B: "Sexagesimal") -> bool:
        return self > B or self == B

    # Less Than or Equal To
    def __le__(self, B: "Sexagesimal") -> bool:
        return self < B or self == B

    # Copy Function
    def __copy__(self) -> "Sexagesimal":
        num = Sexagesimal(self.S)
        num.negative = self.negative
        return num

    # Custom Split function for our Sexagesimal class
    def split(self, sep: str = " ") -> list:

        # Split the string
        return self.S.split(sep)

    # Perform Subtraction with borrow method
    def subtraction_with_borrow(self, greater_D, greater_F, lesser_D, lesser_F):

        # Start with the fractional part
        # We use the most basic algorithm for subtraction of two numbers
        # Subtract the smaller number from the bigger number
        F = []  # To Store the result of fractional part addition
        while len(greater_F) > 0:

            a, b = greater_F.pop(), lesser_F.pop()

            if a < b:

                # If no fractional part is left, then we borrow from the Degrees part
                try:
                    greater_F[-1] -= 1
                except IndexError:
                    greater_D[-1] -= 1

                a += 60

            Diff = (
                a - b
            )  # Rest assured that the difference will never be greater than 59

            # Add the difference to the result list
            F = [f"{Diff:0>2}"] + F

        # Same for Degrees part
        D = []
        while len(greater_D) > 0:

            a, b = greater_D.pop(), lesser_D.pop()

            # Borrow if required
            if a < b:
                greater_D[-1] -= 1
                a += 60

            Diff = a - b

            D = [f"{Diff:0>2}"] + D

        # Join and return the result
        D = ",".join(D)
        F = ",".join(F)
        return Sexagesimal("-" + ";".join([D, F]))

    ## Helper functions  ##
    # Process negative numbers
    def process_negative(self, S: str) -> str:

        # If it is negative set negative as True and remove the negative sign
        if S[0] == "-":
            self.negative = True
            S = S[1:]

        else:
            self.negative = False

        return S

    # Check if number is decimal and convert to sexagesimal
    def check_and_convert_decimal(self, S: str) -> str:

        # If the number is decimal, convert to sexagesimal
        # Here we check if its is Sexagesimal (contains a ";")
        # If not sexagsimal, then it is considered decimal
        if ";" not in S:
            S = (self.Decimal2Sexagesimal(S, 20 + len(S))).S

        return S

    # Check if S is a valid sexagesimal number
    def is_valid_sexagesimal(self, S: str) -> bool:

        # Split into Degrees and Fraction
        Degrees, Fractions = S.split(";")

        # If Degree has a "," then split it into a list
        Deg = Degrees.split(",") if "," in Degrees else [Degrees]

        # If Deg is only one element, then it is considered to be a decimal
        # Hence convert that to base 60
        if len(Deg) == 1:
            N = int(Deg.pop(0))
            while N > 59:
                R = N % 60
                N = N // 60
                Deg = [f"{R:0>2}"] + Deg

            Deg = [f"{N:0>2}"] + Deg

        #  If not, then check if all the elements are less than 60
        else:
            for i in Deg:
                if int(i) >= 60:
                    return False, ValueError(
                        "Invalid Sexagesimal Number: Degrees Part has a value greater than 60"
                    )

        # Similarly for Fractions
        Frac = Fractions.split(",") if "," in Fractions else [Fractions]

        # Check if all the elements are less than 60
        for i in Frac:
            if int(i) >= 60:
                return False, ValueError(
                    "Invalid Sexagesimal Number: Fraction Part has a value greater than 60"
                )

        return True, None

    # Standardize the Sexagesimal Number
    def Standardize(self, S: str) -> str:

        # Split the Sexagesimal Number into Degrees and Fractions
        Degrees, Fractions = S.split(";")

        # If Degree has a "," then split it into a list
        Deg = Degrees.split(",") if "," in Degrees else [Degrees]

        # Similarly for Fractions
        Frac = Fractions.split(",") if "," in Fractions else [Fractions]

        # Join the Degrees and Fractions
        value = ";".join(
            [
                ",".join([f"{d.strip():0>2}" for d in Deg]),
                ",".join([f"{f.strip():0>2}" for f in Frac]),
            ]
        )

        # Remove sign from zero
        value = value.replace("-00", "00")

        return value

    # Convert the given Degree or Fractional part to list
    def input2List(self, Input: str) -> List[str]:

        # Split the String and Convert each element to positive integer
        return [abs(int(x)) for x in Input.split(",")]

    # Make the degree and fractional parts of the two numbers equal length (string length for ease of use)
    def makeEqualLen(
        self, A: "Sexagesimal", B: "Sexagesimal"
    ) -> Tuple["Sexagesimal", "Sexagesimal"]:

        # Split the Sexagesimal Numbers into Degrees and Fractions
        A = str(A).split(";")
        B = str(B).split(";")

        # Split the Degrees and Fractions into lists
        A_D, A_F = A[0].split(","), A[1].split(",")
        B_D, B_F = B[0].split(","), B[1].split(",")

        # Compare lengths and add "00" to the shorter list
        if len(A_D) < len(B_D):
            m = len(B_D) - len(A_D)
            A_D = m * ["00"] + A_D
        else:
            m = len(A_D) - len(B_D)
            B_D = m * ["00"] + B_D

        if len(A_F) < len(B_F):
            m = len(B_F) - len(A_F)
            A_F += m * ["00"]
        else:
            m = len(A_F) - len(B_F)
            B_F += m * ["00"]

        # Join the lists
        A_D = ",".join(A_D)
        A_F = ",".join(A_F)
        B_D = ",".join(B_D)
        B_F = ",".join(B_F)

        # Join the Degrees and Fractions
        A = ";".join([A_D, A_F])
        B = ";".join([B_D, B_F])

        return A, B

    # Convert the Degrees (Base 60 Formate) to Decimal
    def Degrees2Decimal(Input: "Sexagesimal") -> str:

        A_D, A_F = Input.split(";")
        A_D = A_D.split(",")

        Dec = 0
        for i in range(len(A_D)):

            Dec += int(A_D[-(i + 1)]) * (60**i)

        return f"{Dec};{A_F}"

    # Round off the given Sexagesimal Number to the given precision
    @staticmethod
    def RoundOff(Number: Union["Sexagesimal", str], precision: int) -> "Sexagesimal":

        if precision < 0:
            return Number

        try:
            D, F = Number.split(";")
        except AttributeError:  # If Number is not a Sexagesimal Number, just a string
            D, F = Number.split(";")

        F = F.split(",")

        if len(F) <= precision:
            return Number

        carry = 0
        if int(F[precision]) > 29:
            F[precision - 1] = f"{int(F[precision-1]) + 1:0>2}"
            F = F[:precision]

            if precision == 0:
                carry = 1

        else:
            F = F[:precision]

        D = D.split(",")
        if carry == 1:
            D[-1] = f"{int(D[-1]) + 1:0>2}"

        while True:

            if "60" in D:
                D = D[::-1]
                i = D.index("60")
                D[i] = "00"
                D[i + 1] = f"{int(D[i + 1]) + 1:0>2}"
                D = D[::-1]
            else:
                break

        Number = Sexagesimal(f"{','.join(D)};{','.join(F)}")

        if "60" in Number.S:
            return Sexagesimal.RoundOff(Number, precision - 1)
        else:
            return Number

    # Get the reciprocal of the given Sexagesimal Number, upto the given precision (if non-terminating)
    @staticmethod
    def getReciprocal(N: int, precision: int = 99):

        if precision < 99:
            precision = 99

        Sexa = []
        Recur = ""
        Dividend = 1
        pairs = dict()
        flag = False

        while Dividend != 0:

            if N > Dividend:
                Sexa.append("00")
                Dividend *= 60
                continue

            # Dividend *= 60
            Quo = Dividend // N
            Rem = Dividend % N

            Quo = f"{Quo:0>2}"

            if Quo in pairs and Rem in pairs[Quo] and flag is False:
                Recur = Sexa[::-1]
                i = Recur.index(Quo)
                Recur[i] = "(" + Recur[i]
                Recur[0] += ")"
                Recur.reverse()
                flag = True
                Recur = f"{Recur[0]};{','.join(Recur[1:])}"

            if Quo not in pairs:
                pairs[Quo] = [Rem]
            elif Rem not in pairs[Quo]:
                pairs[Quo].append(Rem)

            Sexa.append(f"{Quo:0>2}")
            Dividend = Rem

            Dividend *= 60
            if len(Sexa) > precision:
                flag = True
                break

        if len(Sexa) == 1:
            Sexa.append("00")

        if flag:
            return (f"{Sexa[0]};{','.join(Sexa[1:])}", Recur, flag)
        else:
            return (Sexagesimal(f"{Sexa[0]};{','.join(Sexa[1:])}"), Recur, flag)

    # Convert the given Sexagesimal Number to its Rational Form
    @staticmethod
    def getRationlForm(Number: Union["Sexagesimal", str]):

        try:
            Number: str = Number.S
        except AttributeError:  # If Number is just a string, just pass it on
            pass

        D, F = Number.split(";")
        D = D.split(",")
        F = F.split(",")

        F_R = []
        for i in range(len(F)):
            F_R.append(Rational(int(F[i]), int(pow(60, i + 1))))

        D_R = []
        for i in range(len(D)):
            D_R.append(Rational(int(D[-(i + 1)]) * int(pow(60, i))))

        R = D_R + F_R
        return sum(R)

    # Convert the given Decimal Number to Sexagesimal
    @staticmethod
    def Decimal2Sexagesimal(
        Input: Union[int, float, str], Accuracy: int = 20
    ) -> "Sexagesimal":
        Input = str(Input)
        getcontext().prec = 100

        if "." not in Input:
            Input += ".0"

        D, F = str(Input).split(".")

        if Accuracy <= len(F):
            F = str(F[:Accuracy])

        # Convert the Integral part into sexagesimal
        N = int(D)
        D = []
        while N > 59:
            R = N % 60
            N = N // 60
            D = [f"{R:0>2}"] + D
        D = [f"{N:0>2}"] + D

        # Convert the Fractional part into sexagesimal
        N = str(F)
        F = []

        while len(F) <= Accuracy:

            try:
                M = str(Decimal(N) * 60)
                m = len(N) - len(M)
                M = "0" * m + M
            except InvalidOperation:  # if N == ''
                N += "0"
                continue

            k = len(M) - len(N)

            R = M[:k]
            N = M[k:]
            if R == "":
                R == "00"

            F += [f"{R:0>2}"]

        D = ",".join(D)
        F = ",".join(F)

        while F[-3:] == ",00":
            F = F[:-3]

        result = Sexagesimal(D + ";" + F)

        return result

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

    # Convert the Sexagesimal to a Decimal number
    @staticmethod
    def Sexagesimal2Decimal(Input: Union["Sexagesimal", str], precision: int = 20):

        if isinstance(type(Input), type(Sexagesimal("1"))):
            A = Input.S
            if Input.negative:
                minus = True
            else:
                minus = False
        else:
            A = Input.strip()
            if A[0] == "-":
                minus = True
                A = A[1:]
            else:
                minus = False

        if ";" not in A:
            A = f"{A};00"

        # Get the Decimal and Fractional Part
        A_D, A_F = A.split(";")
        A_D = A_D.split(",")
        A_F = A_F.split(",")

        try:
            D = Decimal("0")
            for i in range(len(A_D)):
                D += Decimal(A_D[-(i + 1)]) * (60**i)

            extra = len(str(D))
            getcontext().prec = precision + extra

            F = Decimal("0")
            for i in range(len(A_F)):
                F += Decimal(A_F[i]) / (60 ** (i + 1))

            F = str(F)

            for i in range(len(F)):
                k = len(F) - i
                if F[i:] == "".join(str(z) for z in [0] * k):
                    F = "".join(list(F[:i]))

                    if F.strip() == "":
                        F = Decimal("0")
                    else:
                        F = Decimal(F)
                    break

            F = Decimal(F)

            # N = str(D) + F[1:]
            N = D + F
            if minus:
                return f"-{N}"
            else:
                return f"{N}"
        except Exception as e:
            print(e)

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

        Details += "\n\n\n\n**Step 1:** Break the Sexagesimal Numbers in their Intergral and Fractional Parts respectively."
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
                Details += f"\n\t{f:0>2}  *  {A_f:0>2}  +  {carry_old:0>2}\t=\t{60*carry + prod:0>2}\t=\t60 * {carry:0>2} + {prod:0>2}"

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
                Details += f"\n\t{f:0>2}  *  {A_d:0>2}  +  {carry_old:0>2}\t=\t{60*carry + prod:0>2}\t=\t60 * {carry:0>2} + {prod:0>2}"

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
                Details += f"\n\t{d:0>2}  *  {A_f:0>2}  +  {carry_old:0>2}\t=\t{60*carry + prod:0>2}\t=\t60 * {carry:0>2} + {prod:0>2}"

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
                Details += f"\n\t{d:0>2}  *  {A_d:0>2}  +  {carry_old:0>2}\t=\t{60*carry + prod:0>2}\t=\t60 * {carry:0>2} + {prod:0>2}"

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

        Details += f"\n\t{'='*(len(Row)+6)}"
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
        if (A.negative is True and B.negative is False) or (
            A.negative is False and B.negative is True
        ):
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
        Details += f"\t \t \t{'-' * (len(B_Num)+2)}"
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
