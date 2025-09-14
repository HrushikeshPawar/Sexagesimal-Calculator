# Basic Usage

The core of the library is the `sexagesimal_calculator.Sexagesimal` class.

### Initialization

You can create a `Sexagesimal` number from several different types, making it easy to integrate into your projects.

```python
from sexagesimal_calculator import Sexagesimal

# From a standard sexagesimal string
s1 = Sexagesimal("10;15,30")
print(s1)
# 10;15,30

# From an integer
s2 = Sexagesimal(3661) # 3600 + 60 + 1
print(s2)
# 01,01,01;00

# From a float
s3 = Sexagesimal(2.75)
print(s3)
# 02;45

# From a negative number
s4 = Sexagesimal("-1;30")
print(s4)
# -01;30
```

### Accessing Parts

You can access the normalized internal parts of a number via its properties.

```python
s = Sexagesimal("-10;15,30")

print(s.is_negative)
# True

print(s.integer_part)
# (10,)

print(s.fractional_part)
# (15, 30)
```

### Error Handling

The library will raise specific, descriptive errors for invalid operations.

-   **`InvalidFormatError`**: Raised during initialization if a string cannot be parsed as a valid sexagesimal or decimal number, or if any part is `>= 60`.

```python
>>> from sexagesimal_calculator import Sexagesimal
>>> from sexagesimal_calculator.exceptions import InvalidFormatError
>>> try:
...     s = Sexagesimal("10;65")
... except InvalidFormatError as e:
...     print(e)
...
Fraction Part has a value greater than 60
```

-   **`ZeroDivisionError`**: Raised when attempting to divide by zero.

```python
>>> a = Sexagesimal(10)
>>> b = Sexagesimal(0)
>>> a / b
Traceback (most recent call last):
  ...
ZeroDivisionError: Division by zero is not allowed.
```