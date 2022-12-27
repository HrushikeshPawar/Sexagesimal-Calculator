# Sexagesimal Calculator

The Sexagesimal Calculator performs all the required calculations on sexagesimal coordinates. During the calculations, all the intermediate steps are performed in sexagesimal number system and no sort of conversion to decimal number system takes place in the background.

This was developed for the summer project for the  [HoMI](https://sites.iitgn.ac.in/homi/) (History of Mathematics in India) initiative at [Indian Institute of Technology, Gandhinagar](https://iitgn.ac.in/). For more information about this project see the [Indian Numerical Decoding and Encoding Applications](https://students.iitgn.ac.in/homi-project) page.

## Installation

You can install the Sexagesimal Calculator from [PyPI](https://pypi.org/project/sexagesimal-calculator/):

    python -m pip install sexagesimal-calculator

## How to use
     
    >>> from sexagesimal_calculator.sexagesimal import Sexagesimal
    >>> A = Sexagesimal(289)
    >>> A
    04,49;00
    >>> A = Sexagesimal('289')
    >>> A
    04,49;00
    >>> B = Sexagesimal('4;34,54')
    >>> B
    04;34,54
    >>> C = Sexagesimal('5;456')
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "C:\Users\hrush\OneDrive - iitgn.ac.in\Desktop\sexagesimal-calculator\sexagesimal_calculator\sexagesimal.py", line 51, in __init__
        raise Exception("Fractional Part has 60+ entry")
    Exception: Fractional Part has 60+ entry

### 1. Decimal to Sexagesimal Converter (Input should be decimal number.)
- Allowed inputs - `1, 0.23, .23, 1.0`
- Use `Sexagesimal.Decimal2Sexagesimal(Input, Accuracy=20)`
- **Accuracy** (optional) : 
    - The number of digits to consider after the decimal point.
    - Default value is 20 (digits after decimal point).
    - Example : If input is `1.23456` and accuracy is `2`, then the program will consider only `1.23` for conversion.

```
>>> A = Sexagesimal(1.23456)
01;14,04,24,57,36
>>> Sexagesimal.Decimal2Sexagesimal(1.23456, 2)
01;13,48
>>> Sexagesimal.Decimal2Sexagesimal(1.23)
01;13,48
```

---

### 2. Sexagesimal to Decimal Converter:
- Input should be a sexagesimal number.
- ` ; ` should be used to separat the intergal part 
- ` , ` should be used to separate the fractional apart.
- Use `Sexagesimal.Sexagesimal2Decimal(Input, precision=20)`
- Example : `12;01,45,12`
- **Precision** (optional) :
    - Number of fractional places to consider in the final result.
    - Examples: 
        - `21;19,53,47,43,29  --->  21.33160983667695473251` (20 decimal places). 
        - But if Precision value is 30, then the result will be `21.331609836676954732510288065844`
    - By default, the program will give result till 20 decimal places.
    - This option is helpful if the given sexagesimal number contains a non-regular number in the fractional part.
```
>>> A = Sexagesimal('21;19,53,47,43,29')
>>> Sexagesimal.Sexagesimal2Decimal(A)                  
'21.33160983667695473251'
>>> Sexagesimal.Sexagesimal2Decimal(A, 30) 
'21.331609836676954732510288065844'
>>> Sexagesimal.Sexagesimal2Decimal(A, 10) 
'21.3316098367'
>>> Sexagesimal.Sexagesimal2Decimal(A, 50) 
'21.33160983667695473251028806584362139917695473251029'
```

---

### 3. Addition and Subtraction:
- Input can be in the decimal form, sexagesimal form or mixed.
- But the answer will always be in the sexagesimal form
```
>>> Sexagesimal(1.23) + Sexagesimal(4.32) - Sexagesimal(5.32)
00;13,48
>>> Sexagesimal('4;2,45') + Sexagesimal('6;12,1') - Sexagesimal('1,45;12,56,38')
-01,34;58,10,38
>>> Sexagesimal(1.23) + Sexagesimal(4.32) - Sexagesimal('1,45;12,56,38')
-01,39;39,56,38
```

---

### 4. Multiplication:
- Input can be in the decimal form, sexagesimal form or mixed.
- But the answer will always be in the sexagesimal form
```
>>> Sexagesimal(1.23) + Sexagesimal(4.32) - Sexagesimal('1,45;12,56,38')
-01,39;39,56,38
>>> Sexagesimal(1.23) * Sexagesimal(- 5.32)
-06;32,36,57,36
>>> Sexagesimal('-4;2,45') * Sexagesimal('-6;12,1')
25;05,07,02,45
>>> Sexagesimal(-4.32) * Sexagesimal('1,45;12,56,38')
-07,34;31,55,03,21,36
```
- **Verbose** (Optional):
    - When selected the program will print every step involved in the calculation.
    - This can be used to check the steps and confirm the correctness.
    - It also shows that all the intermediate calculations are done in sexagesimal number system and there is no back and forth from the decimal system.
    - Use `Sexagesimal.Multiplication(A, B, verbose=True)`

    ```
    >>> A = Sexagesimal(1.332)
    >>> B = Sexagesimal(3.53)
    >>> res, details = Sexagesimal.Multiplication(A, B, True)
    >>> res
    04;42,07,03,21,36
    >>> print(details)
    ```

---

### 5. Division:
- The inputs (Dividend and Divisor) can be decimal, sexagesimal or mixed.
- But the answer will always be in the sexagesimal form.
```
>>> Sexagesimal(3.24) / Sexagesimal(6.12)
00;31,45,52,56,28,14,07,03,31,45,52,56,28,14,07,03,31,45,52,56
>>> Sexagesimal('03;14,24') / Sexagesimal('06;07,12')
00;31,45,52,56,28,14,07,03,31,45,52,56,28,14,07,03,31,45,52,56
>>> Sexagesimal(3.24) / Sexagesimal('6;04')
00;32,02,38,14,30,19,46,48,47,28,21,05,56,02,38,14,30,19,46,49
```
- **Precision** :
    - By default, the program prints final answer upto 20 fractional places.
    - This option could be used to increase or decrease the number of fractional places to be displayed in the final answer.
    ```
    >>> A = Sexagesimal(3.24)
    >>> B = Sexagesimal('6;04')
    >>> Sexagesimal.Division(A, B)
    00;32,02,38,14,30,19,46,48,47,28,21,05,56,02,38,14,30,19,46,49
    >>> Sexagesimal.Division(A, B, precision=10)
    00;32,02,38,14,30,19,46,48,47,28
    >>> Sexagesimal.Division(A, B, precision=30)
    00;32,02,38,14,30,19,46,48,47,28,21,05,56,02,38,14,30,19,46,48,47,28,21,05,56,02,38,14,30,20
    ```
- **Verbose** :
    - When selected the program will print every step involved in the calculation.
    - This can be used to check the steps and confirm the correctness.
    - Use `Sexagesimal.Division(A, B, verbose=True)`
    ```
    >>> A = Sexagesimal(3.24)
    >>> B = Sexagesimal('6;04')
    >>> res, details = Sexagesimal.Division(A, B, verbose=True) 
    >>> res
    00;32,02,38,14,30,19,46,48,47,28,21,05,56,02,38,14,30,19,46,49
    >>> print(details)
    ```

---

### 6. Increment Table Generator:
- Used to create the addition and subtraction tables.
- The Initial value and the Increment value can be in decimal, sexagesimal or mixed form.
- The Row and Mod has to be a positive integer.
- If mod is less than 2, then the integral part of values will be a decimal and will not be moded.
- Use `IncrementTableGenerator(Inc_Initial, Inc_Increment, Inc_Rows=10, Inc_Mod=60)`

```
>>> Sexagesimal.IncrementTableGenerator('10;10', '20;10', 15, 60)
['10;10', '30;20', '50;30', '10;40', '30;50', '51;00', '11;10', '31;20', '51;30', '11;40', '31;50', '52;00', '12;10', '32;20', '52;30', '12;40']
>>> Sexagesimal.IncrementTableGenerator('10;10', '20;10', 15, 30)
['10;10', '00;20', '20;30', '10;40', '00;50', '21;00', '11;10', '01;20', '21;30', '11;40', '01;50', '22;00', '12;10', '02;20', '22;30', '12;40']
>>> Sexagesimal.IncrementTableGenerator('10;10', '20;10', 15, 90)
['10;10', '30;20', '50;30', '70;40', '0;50', '21;00', '41;10', '61;20', '81;30', '11;40', '31;50', '52;00', '72;10', '2;20', '22;30', '42;40']
```
