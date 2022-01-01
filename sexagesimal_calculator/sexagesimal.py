from decimal import *
from sympy import Rational
from math import pow

class Sexagesimal:

    def __init__(self, S):

        S = str(S).strip()

        self.S = S

        if S[0] == "-":
            self.negative = True
            S = S[1:].strip()
        else:
            self.negative = False
        
        if ";" not in S:
            S = (self.Decimal2Sexagesimal(S, 20+len(S))).S

        S_D, S_F = S.split(";")

        D, F = [], []
        for d in S_D.split(","):
            D.append(f'{d:0>2}')
        
        for f in S_F.split(","):
            F.append(f'{f:0>2}')
        
        N = int(D.pop(0))
        while N > 59:
            R = N % 60
            N = N //  60
            D = [f"{R:0>2}"] + D
        
        D = [f"{N:0>2}"] + D

        Inputs = D + F
        for n in Inputs:
            if int(n) > 59:
                raise Exception("Fractional Part has 60+ entry")

        D, F = ",".join([d.strip() for d in D]), ",".join([f.strip() for f in F])
        
        S = f"{D};{F}"

        self.S = S
    
    def __repr__(self):
        S = self.S
        
        if self.negative:
            S = "-" + S
        
        return S
    
    def __add__(self, B):

        # Get the terms
        A = self

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

        # Add the Decimal part
        if A.negative and B.negative:
            F = []
            carry = 0
            while len(A_F) > 0:

                a, b = A_F.pop(), B_F.pop()
                Sum = a + b + carry

                if Sum >= 60:
                    Sum -= 60
                    carry = 1
                else:
                    carry = 0
                
                F = [f"{Sum:0>2}"] + F

            # Add the integral part
            D = []
            while len(A_D) > 0:

                a, b = A_D.pop(), B_D.pop()
                Sum = a + b + carry

                if Sum >= 60:
                    Sum -= 60
                    carry = 1
                else:
                    carry = 0
                
                D = [f"{Sum:0>2}"] + D
            
            #print(carry)
            
            D = ",".join(D)
            F = ",".join(F)

            return Sexagesimal("-" + ";".join([D, F]))      
        
        elif A.negative == True and B.negative == False:
            A = Sexagesimal(A.S)
            A.negative = False
            return B - A

        elif A.negative == False and B.negative == True:
            B = Sexagesimal(B.S)
            B.negative = False
            return A - B

        else:
            F = []
            carry = 0
            while len(A_F) > 0:

                a, b = A_F.pop(), B_F.pop()
                Sum = a + b + carry

                if Sum >= 60:
                    Sum -= 60
                    carry = 1
                else:
                    carry = 0
                
                F = [f"{Sum:0>2}"] + F

            # Add the integral part
            D = []
            while len(A_D) > 0:

                a, b = A_D.pop(), B_D.pop()
                Sum = a + b + carry

                if Sum >= 60:
                    Sum -= 60
                    carry = 1
                else:
                    carry = 0
                
                D = [f"{Sum:0>2}"] + D
            
            if carry == 1:
                D = ["01"] + D

            D = ",".join(D)
            F = ",".join(F)

            return Sexagesimal(";".join([D, F]))    

    def __sub__(self, B):

        # Get the terms
        A = self

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

        if A.negative == False and B.negative == False:
            
            if len(A_D) > len(B_D) or A > B:

                F = []
                carry = 0
                while len(A_F) > 0:

                    a, b = A_F.pop(), B_F.pop()

                    if a < b:

                        try:
                            A_F[-1] -= 1
                        except:
                            A_D[-1] -= 1
                        
                        a += 60
                    
                    Diff = a - b + carry

                    if Diff >= 60:
                        Diff -= 60
                        carry = 1
                    else:
                        carry = 0
                    
                    F = [f"{Diff:0>2}"] + F

                # Add the integral part
                D = []
                while len(A_D) > 0:

                    a, b = A_D.pop(), B_D.pop()

                    if a < b:
                        A_D[-1] -= 1
                        a += 60
                    

                    Diff = a - b + carry

                    if Diff >= 60:
                        Diff -= 60
                        carry = 1
                    else:
                        carry = 0
                    
                    D = [f"{Diff:0>2}"] + D
                
                D = ",".join(D)
                F = ",".join(F)

                return Sexagesimal(";".join([D, F]))    
            
            else:
                
                F = []
                carry = 0
                while len(A_F) > 0:

                    a, b = A_F.pop(), B_F.pop()

                    if b < a:

                        try:
                            B_F[-1] -= 1
                        except:
                            B_D[-1] -= 1
                        
                        b += 60
                    
                    Diff = b - a + carry

                    if Diff >= 60:
                        Diff -= 60
                        carry = 1
                    else:
                        carry = 0
                    
                    F = [f"{Diff:0>2}"] + F

                # Add the integral part
                D = []
                while len(A_D) > 0:
                    a, b = A_D.pop(), B_D.pop()
                
                    if b < a:
                        
                        B_D[-1] -= 1
                        b += 60
                    

                    Diff = b - a + carry

                    if Diff >= 60:
                        Diff -= 60
                        carry = 1
                    else:
                        carry = 0
                    
                    D = [f"{Diff:0>2}"] + D
                
                D = ",".join(D)
                F = ",".join(F)

                return Sexagesimal("-" + ";".join([D, F]))    

        elif A.negative == True and B.negative == False:

            B = Sexagesimal(f"-{B.S}")
            return A + B
        
        elif B.negative == True and A.negative == False:

            B = Sexagesimal(f"-{B.S}")
            return A + B

        else:

            B = Sexagesimal(f"-{B.S}")
            return B + A

    def __mul__(self, B):

        # # Get terms
        # A = self
        # A_S = self.S
        # B_S = B.S

        # # Break into integral and fractional part
        # A_D, A_F = A_S.split(";")
        # B_D, B_F = B_S.split(";")
        
        # # Make lists for integral and fractional part
        # A_D = A_D.split(",")
        # A_F = A_F.split(",")
        # B_D = B_D.split(",")
        # B_F = B_F.split(",")

        # # Multiply the fractional part
        # Multiplication = []
        # for f in B_F[::-1]:
        #     carry = 0
        #     f = int(f)
        #     i = len(Multiplication)

        #     if i == 0:
        #         Multiplication.append([])
        #     else:
        #         Multiplication.append(i * [0])
            
        #     for A_f in A_F[::-1]:
        #         A_f = int(A_f)
        #         prod = f * A_f + carry
                
        #         if prod > 59:
        #             carry = prod // 60
        #             prod %= 60
        #         else:
        #             carry = 0
                
        #         Multiplication[i] = [prod] + Multiplication[i]

        #     for A_d in A_D[::-1]:
        #         A_d = int(A_d)
        #         prod = f * A_d + carry
                
        #         if prod > 59:
        #             carry = prod // 60
        #             prod %= 60
        #         else:
        #             carry = 0
                
        #         Multiplication[i] = [prod] + Multiplication[i]

        #     if carry > 0:
        #         while carry > 59:
        #             R = carry % 60
        #             carry = carry //  60
        #             Multiplication[i] = [R] + Multiplication[i]
        #         Multiplication[i] = [carry] + Multiplication[i]
        
        # # Multiply the intger part
        # for d in B_D[::-1]:
        #     d = int(d)
        #     carry = 0
        #     i = len(Multiplication)

        #     if i == 0:
        #         Multiplication.append([])
        #     else:
        #         Multiplication.append(i * [0])
            
        #     for A_f in A_F[::-1]:
        #         A_f = int(A_f)
        #         prod = d * A_f + carry
                
        #         if prod > 59:
        #             carry = prod // 60
        #             prod %= 60
        #         else:
        #             carry = 0
                
        #         Multiplication[i] = [prod] + Multiplication[i]

        #     for A_d in A_D[::-1]:
        #         A_d = int(A_d)
        #         prod = d * A_d + carry
                
        #         if prod > 59:
        #             carry = prod // 60
        #             prod %= 60
        #         else:
        #             carry = 0
                
        #         Multiplication[i] = [prod] + Multiplication[i]

        #     if carry > 0:
        #         while carry > 59:
        #             R = carry % 60
        #             carry = carry //  60
        #             Multiplication[i] = [R] + Multiplication[i]
        #         Multiplication[i] = [carry] + Multiplication[i]
        
        # # Make all rows of same length
        # max_lenght = max([len(x) for x in Multiplication])
        # for i in range(len(Multiplication)):

        #     m = max_lenght - len(Multiplication[i])

        #     Multiplication[i] = m*[0] + Multiplication[i]
        

        # Result = []
        # carry = 0
        # for i in list(range(len(Multiplication[0])))[::-1]:

        #     elems = []
        #     for j in range(len(Multiplication)):
        #         elems.append(Multiplication[j][i])
        #     Sum = sum(elems) + carry

        #     if Sum > 59:
        #         carry = Sum // 60
        #         Sum %= 60
        #     else:
        #         carry = 0
            
        #     Result = [f"{Sum:0>2}"] + Result

        # #print(Result, carry)
        # if carry > 0:
        #     while carry > 59:
        #         R = carry % 60
        #         carry = carry //  60
        #         Result = [f"{R:0>2}"] + Result
        #     Result = [f"{carry:0>2}"] + Result

        # k = len(A_F) + len(B_F)
        
        # D, F = Result[:-k], Result[-k:]
        # #print(D, F, k)
        # D = ",".join(D)
        # F = ",".join(F)


        # while F[-3:] == ",00":
        #     F = F[:-3]
        
        # while D[:3] == "00,":
        #     D = D[3:]

        # #print(A.negative, B.negative)
        # if (A.negative == True and B.negative == False) or (A.negative == False and B.negative == True):
        #     return Sexagesimal(f"-{D};{F}")
        # else:
        #     return Sexagesimal(f"{D};{F}")
        return self.Multiplication(self, B)

    def __truediv__(self, B):

        # A = self
        
        # # Get Rational Form of B
        # try:
        #     B_Num, B_Denom = str(self.getRationlForm(B)).split("/")
        # except:
        #     B_Num = str(self.getRationlForm(B))
        #     B_Denom = 1
        
        # # Get Reciprocal of the B_Num
        # B_Num_R, Recur, flag = self.getReciprocal(int(B_Num))
        # B_Num_R1 = Sexagesimal(B_Num_R)
        # B_Denom = Sexagesimal(B_Denom)

        # # Now we get the Reciprocal of B
        # B_R = B_Num_R1 * B_Denom

        # # And now we do the actual divison. Which is nothing but multiplication with the reciprocal
        # Div = A * B_R

        # if A.negative and B.negative == False:
        #     Div.negative = True
        # elif A.negative == False and B.negative:
        #     Div.negative = True
        # else:
        #     Div.negative = False
        
        # if len(Div.S.split(";")[1].split(",")) > 20:
        #     Div = Sexagesimal.RoundOff(Div, 20)
        
        # return Div
        return self.Division(self, B)

    def __neg__(self):
        if self.negative == True:
            return Sexagesimal(self.S)
        else:
            return Sexagesimal(f"-{self.S}")
    
    def __pos__(self):

        if self.negative:
            return Sexagesimal(f"-{self.S}")
        else:
            return Sexagesimal(self.S)
        
    def __pow__(self, n):

        A = self

        for i in range(n-1):
            A *= A
        return A

    def __iadd__(self, B):
        A = self
        return A + B

    def __isub__(self, B):
        A = self
        return A - B

    def __imul__(self, B):
        A = self
        return A * B

    def __gt__(self, B):

        A = self

        if A.negative and B.negative == False:
            return False
        
        if A.negative == False and B.negative == True:
            return True
        
        if A.negative and B.negative:

            A_D, A_F = A.S.split(";")
            B_D, B_F = B.S.split(";")

            if len(A_D) > len(B_D):
                return False
            
            if len(A_D) < len(B_D):
                return True

            for i in range(len(A_D)):
                if A_D[i] > B_D[i]:
                    return False
                
                if B_D[i] > A_D[i]:
                    return True
                
            for i in range(len(A_F)):
                if A_F[i] > B_F[i]:
                    return False
                
                if B_F[i] > A_F[i]:
                    return True
            
            return False
        
        A_D, A_F = A.S.split(";")
        B_D, B_F = B.S.split(";")

        if len(A_D) > len(B_D):
            return True
        
        if len(A_D) < len(B_D):
            return False

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
        
        return True
    

    # Helping Functions
    def input2List(self, Input):
        L = Input.split(",")
        L = [abs(int(x)) for x in L]
        
        return L

    def makeEqualLen(self, A, B):
    
        A = str(A).split(";")
        B = str(B).split(";")

        A_D, A_F = A[0].split(","), A[1].split(",")
        B_D, B_F = B[0].split(","), B[1].split(",")

        if len(A_D) < len(B_D):
            m = len(B_D) - len(A_D)
            A_D = m*["00"] + A_D  
        else:
            m = len(A_D) - len(B_D)
            B_D = m*["00"] + B_D

        if len(A_F) < len(B_F):
            m = len(B_F) - len(A_F)
            A_F += m*["00"]
        else:
            m = len(A_F) - len(B_F)
            B_F += m*["00"]
        
        A_D = ",".join(A_D)
        A_F = ",".join(A_F)
        B_D = ",".join(B_D)
        B_F = ",".join(B_F)

        A = ";".join([A_D, A_F])
        B = ";".join([B_D, B_F])

        return (A, B)

    def Integral2Decimal(Input):
        
        A_D, A_F = Input.S.split(";")
        A_D = A_D.split(",")
        
        Dec = 0
        for i in range(len(A_D)):
            
            Dec += int(A_D[-(i+1)]) * (60 ** i)
        
        return f"{Dec};{A_F}"


    @staticmethod
    def RoundOff(Number, precision):
        #print(precision)
        
        if precision < 0:
            return Number
        
        try:
            D, F = Number.S.split(";")
        except:
            D, F = Number.split(";")

        F = F.split(',')

        if len(F) <= precision:
            return Number

        carry = 0
        if int(F[precision]) > 29:
            F[precision-1] = f"{int(F[precision-1]) + 1:0>2}"
            F = F[:precision]

            if precision == 0:
                carry = 1

        else:
            F = F[:precision]
        
        D = D.split(',')
        if carry == 1:
            D[-1] = f"{int(D[-1]) + 1:0>2}"
        
        while True:
            
            if "60" in D:
                D = D[::-1]
                i = D.index("60")
                D[i] = "00"
                D[i+1] = f"{int(D[i+1]) + 1:0>2}"
                D = D[::-1]
            else:
                break
        
            

        Number =  Sexagesimal(f"{','.join(D)};{','.join(F)}")
        
        if "60" in Number.S:
            return Sexagesimal.RoundOff(Number, precision-1)
        else:
            return Number
        
    @staticmethod
    def getReciprocal(N, precision=99):
        
        if precision < 99:
            precision = 99

        Sexa = []
        Recur = ''
        Dividend = 1
        pairs = dict()
        flag = False
        
        while Dividend != 0:

            if N > Dividend:
                Sexa.append("00")
                Dividend *= 60
                continue
            
            
            #Dividend *= 60
            Quo = Dividend // N
            Rem = Dividend % N
            
            Quo = f"{Quo:0>2}"

            if Quo in pairs and Rem in pairs[Quo] and flag == False:
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

            #print(Sexa, Dividend)
            Dividend *= 60
            #print(Sexa, Dividend)
            if len(Sexa) > precision:
                flag = True
                break
        
        #print(f"Dividend : {Dividend}\nlen(Sexa) : {len(Sexa)}\nFlag : {flag}\nPrecision : {precision}")
        if len(Sexa) == 1:
            Sexa.append("00")
        
        if flag:
            return(f"{Sexa[0]};{','.join(Sexa[1:])}", Recur, flag)
        else:
            return (Sexagesimal(f"{Sexa[0]};{','.join(Sexa[1:])}"), Recur, flag)
    
    @staticmethod
    def getRationlForm(Number):

        try:
            Number = Number.S
        except:
            Number = Number


        D, F = Number.split(";")
        D = D.split(",")
        F = F.split(",")

        F_R = []
        for i in range(len(F)):
            F_R.append(Rational(int(F[i]), int(pow(60, i+1))))
        
        D_R = []
        for i in range(len(D)):
            D_R.append(Rational(int(D[-(i+1)]) * int(pow(60, i))))
        
        R = D_R + F_R
        return sum(R)

    @staticmethod
    def Decimal2Sexagesimal(Input, Accuracy=20):
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
            N = N //  60
            D = [f"{R:0>2}"] + D
        D = [f"{N:0>2}"] + D

        # Convert the Fractional part into sexagesimal
        N = str(F)
        F = []
        
        while len(F) <= Accuracy:

            try:
                M = str(Decimal(N) * 60)
                m = len(N) - len(M)
                M = "0"*m + M
            except:
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

    @staticmethod
    def mod60ToMod(Input, mod):

        try:
            A = Input.S
        except:
            print("Not a Sexagesimal Object")
            return

        
        A_D, A_F = A.split(";")
        A_D = A_D.split(",")

        New_A_D = []
        for i in range(len(A_D)):

            elem = A_D[-(i+1)]
            New_A_D.append(int(elem)*(60**i))
        
        N = sum(New_A_D)
        D = N % mod

        return f"{D};{A_F}"

    @staticmethod
    def Sexagesimal2Decimal(Input, precision=20):

        if type(Input) == type(Sexagesimal("1")):
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
        
        if ';' not in A:
            A = f'{A};00'
        
        A_D, A_F = A.split(";")
        A_D = A_D.split(",")
        A_F = A_F.split(",")

        try:
            D = Decimal("0")
            for i in range(len(A_D)):
                D += Decimal(A_D[-(i+1)]) * (60**i)

            extra = len(str(D))
            getcontext().prec = precision + extra
                    
            F = Decimal("0")
            for i in range(len(A_F)):
                F += Decimal(A_F[i]) / (60**(i+1))
            
            F = str(F)

            for i in range(len(F)):
                k = len(F) - i
                if F[i:] == ''.join(str(z) for z in [0]*k):
                    F = ''.join(list(F[:i]))
            
                    if F.strip() == '':
                        F = Decimal('0')
                    else:
                        F = Decimal(F)
                    break

            F = Decimal(F)
            
            #N = str(D) + F[1:]
            N = D + F
            if minus:
                return f"-{N}"
            else:
                return f"{N}"
        except Exception as e:
            print(e)

    @staticmethod
    def Multiplication(A, B, verbose=False):

        # Get A and B as right form of Sexagesimal string
        try:
            A_S = A.S
            B_S = B.S
        except:
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
        Details = f"\n\n\n\n**Inputs:**"
        Details += f"\n\n\tA\t=\t{A}"
        Details += f"\n\tB\t=\t{B}"
        
        Details += f"\n\n\n\n**Step 1:** Break the Sexagesimal Numbers in their Intergral and Fractional Parts respectively."
        Details += f"\n\n\tIntegral part of A\t\t=\t{A_D}"
        Details += f"\n\tFractional part of A\t=\t{A_F}"
        Details += f"\n\n\tIntegral part of B\t\t=\t{B_D}"
        Details += f"\n\tFractional part of B\t=\t{B_F}"
        

        # A List to store all the intermediate Multiplication Results
        Multiplication = []

        # Multiply the Fractional part of B with A:
        Details += f"\n\n\n\n**Step 2:** Multiply the fractional part of B to A, one Sexagesimal place at a time.\n"
        for f in B_F[::-1]:
            carry = 0
            f = int(f)
            i = len(Multiplication)

            if i == 0:
                Multiplication.append([])
            else:
                Multiplication.append(i * [0])
            
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
                #print(f"\t{f:0>2}  *  {A_f:0>2}  +  {carry_old:0>2}\t=\t{60*carry + prod:0>2}\t=\t60 * {carry:0>2} + {prod:0>2}")
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
                    carry = carry //  60
                    Multiplication[i] = [R] + Multiplication[i]
                Multiplication[i] = [carry] + Multiplication[i]
            
            Details += f"\n\n\t{f}  *  {A}\t=\t{Multiplication[i]}\n"


        # Multiply the Integral part of B with A:
        Details += f"\n\n\n\n**Step 3:** Multiply the integral part of B to A, one Sexagesimal place at a time.\n"
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
                    carry = carry //  60
                    Multiplication[i] = [R] + Multiplication[i]
                Multiplication[i] = [carry] + Multiplication[i]
            #print(f"\n\t{d}  *  {A}\t=\t{Multiplication[i]}\n")
            Details += f"\n\n\t{d}  *  {A}\t=\t{Multiplication[i]}\n"
        
        # Step 4: Make all the rows of equal length
        Details += f"\n\n\n\n**Step 4:** Make all the rows of equal lenght to get the following matrix of all the intermediate results\n"
        max_lenght = max([len(x) for x in Multiplication])
        for i in range(len(Multiplication)):

            m = max_lenght - len(Multiplication[i])

            Multiplication[i] = m*[0] + Multiplication[i]
        
        for row in Multiplication:
            Row = []
            for elem in row:
                Row.append(f"{elem:0>2}")
            Row = " | ".join(Row)
            #print(f"\t | {Row} |")
            Details += f"\n\t | {Row} |"
        
        # Step 5: Add all the rows, column by column, from right to left
        Details += f"\n\n\n\n**Step 5:** Add all the rows, column by column, from right to left. Following is the final result of addition\n"
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
                carry = carry //  60
                Result = [f"{R:0>2}"] + Result
            Result = [f"{carry:0>2}"] + Result

        for row in Multiplication:
            Row = []
            i = len(Result) - len(row)
            row = ['00']*i + row
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
        Details += f"\n\n\n\n**Step 6:** Divide the result into the Integral and the Fractional Part (Using the length of A_F and B_F)\n"
        
        k = len(A_F) + len(B_F)
        D, F = Result[:-k], Result[-k:]
        D = ",".join(D)
        F = ",".join(F)
        Details += f"\n     Result  =  {D};{F}"

        # Step 7: Strip the trailing or preceeding zeros from the result, if any
        Details  += f"\n\n\n\n**Step 7:** Strip the trailing or preceeding zeros from the result, if any"
        while F[-3:] == ",00":
            F = F[:-3]
        
        while D[:3] == "00,":
            D = D[3:]

        Details += f"\n\n       Result  =  {D};{F}"

        # Step 8: Give proper sign to the Result
        Details += f"\n\n\n\n**Step 8:** Give proper sign to the Result"
        if (A.negative == True and B.negative == False) or (A.negative == False and B.negative == True):
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

    @staticmethod
    def Division(A, B, precision=20, verbose=False):

        # Get A and B as right form of Sexagesimal string
        try:
            A_S = A.S
            B_S = B.S
        except:
            A = Sexagesimal(A)
            B = Sexagesimal(B)
            A_S = A.S
            B_S = B.S
        
        # Print the above details
        Details = f"\n\n\n\n**Inputs:**"
        Details += f"\n\n\tA\t=\t{A}"
        Details += f"\n\tB\t=\t{B}"
            
            
        # Step1 : Get the Rational Form of B
        try:
            B_Num, B_Denom = str(Sexagesimal.getRationlForm(B)).split("/")
        except:
            B_Num = str(Sexagesimal.getRationlForm(B))
            B_Denom = 1

        Details += f"\n\n\nStep 1: Get the rational form of B"
        Details += f"\n\tB\t=\t {B_Num}"
        Details += f"\t \t \t{'-' * (len(B_Num)+2)}"
        Details += f"\t \t \t {B_Denom}"
            
        
        # Step 2: Get Reciprocal of the B_Num
        B_Num_R, Recur, flag = Sexagesimal.getReciprocal(int(B_Num), precision+10)
        B_Num_R1 = Sexagesimal(B_Num_R)

        Details += f"\n\n\nStep 2: Get the reciprocal of the numberator of B (Why? Because, dividing by B is same as multiplying by reciprocal of B)"
        if flag:
            Details += f"\n\tThe numerator of B is not a regular number (i.e has a prime factor other than 2, 3 or 5)."
            Details += f"\tHence, the reciprocal of numberator is non-terminating but recurring! (The recurring term is enclosed on brackets)"
        else:
            Details += f"\n\tThe numerator of B is a regular number. Hence, the reciprocal has an exact Sexagesimal Representation"
        
        if len(Recur) == 0:
            if len(B_Num_R.split(";")[1].split(",")) > precision:
                B_Num_R = Sexagesimal.RoundOff(B_Num_R, precision)
        
            Details += f"\n\tReciprocal of numerator {B_Num}\t=\t{B_Num_R}"
        else:
            Details += f"\n\tReciprocal of numerator {B_Num}\t=\t{Recur}"


        # Step 3: Now we get the Reciprocal of B
        B_Denom = Sexagesimal(B_Denom)
        B_R = B_Num_R1 * B_Denom
        
        Details += f"\n\n\nStep 3: Calculate the Reciprocal of B (Denominator x Reciprocal of Numerator)"
        Details += f"\n\tReciprocal of B (B')\t=\t{B_R}"

        # Step 4: And now we do the actual divison. Which is nothing but multiplication with the reciprocal
        Div = A * B_R
        if A.negative and B.negative == False:
            Div.negative = True
        elif A.negative == False and B.negative:
            Div.negative = True
        else:
            Div.negative = False

        if len(Div.S.split(";")[1].split(",")) > precision:
            Div = Sexagesimal.RoundOff(Div, precision)

        Details += f"\n\n\nStpe 4: Do the actual Division (A/B = A * B')"
        Details += f"\n\tA/B\t=\t{Div}"

        if flag:

            A_D, A_F = A.S.split(";")
            A_D = A_D.split(",")
            A_F = A_F.split(",")
            
            A_New = Div * B
            A_New_D, A_New_F = A_New.S.split(";")
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

        Inc_Initial     = Sexagesimal(Inc_Initial)
        Inc_Increment   = Sexagesimal(Inc_Increment)

        if Inc_Mod < 2:
            Inc_Mod = 0
        
        A = Sexagesimal(Inc_Initial)
        i=0
        Inc_output = []

        if A.negative:
            Inc_output.append(f'-{A.S}')
        else:
            Inc_output.append(A.S)
        
        while i < Inc_Rows:

            B = Sexagesimal(Inc_Increment)
            A = A + B
            
            A_I = Sexagesimal.Integral2Decimal(A)
            A_D, A_F = A_I.split(";")
            
            if Inc_Mod == 0:
                
                if A.negative == True and A.S != "00;00":
                    A = Sexagesimal(f"-{A_D};{A_F}")
                    Inc_output.appned(f"-{Sexagesimal.Integral2Decimal(A)}")
                    
                else:
                    A = Sexagesimal(f"{A_D};{A_F}")
                    Inc_output.append(f"{Sexagesimal.Integral2Decimal(A)}")
                    
            else:
                A_D = int(A_D) % Inc_Mod

                if A.negative == True and A.S != "00;00":
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