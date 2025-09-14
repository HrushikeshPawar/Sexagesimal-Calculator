# Arithmetic Operations

The `Sexagesimal` class supports all standard Python arithmetic operators, allowing for natural and intuitive calculations.

### Addition (`+`)
Performs base-60 addition with full carry propagation.
```python
a = Sexagesimal("59;59")
b = Sexagesimal("0;01")
print(a + b)
# 01,00;00
```

### Subtraction (`-`)
Performs base-60 subtraction with full borrow propagation.
```python
a = Sexagesimal("1,00;00,00")
b = Sexagesimal("0;00,01")
print(a - b)
# 59;59,59
```

### Multiplication (`*`)
Uses a native long multiplication algorithm. The number of fractional places in the result is the sum of the fractional places of the operands.
```python
a = Sexagesimal("1;30")   # 1.5
b = Sexagesimal("0;30")   # 0.5
print(a * b)
# 00;45                  # 0.75
```

### Division (`/`)
Uses exact rational arithmetic to ensure maximum precision, avoiding floating-point errors.
```python
a = Sexagesimal("10;00")
b = Sexagesimal(3)
print(a / b)
# 03;20
```

### Power (`**`)
Supports integer exponents, including negative exponents for calculating reciprocals.
```python
base = Sexagesimal("2;00")
print(base ** 3)
# 08;00

print(base ** -1)
# 00;30
```

### Comparison Operators

You can compare `Sexagesimal` numbers using standard Python comparison operators.

```python
a = Sexagesimal("10;30")
b = Sexagesimal(10.5)
c = Sexagesimal("-5;00")

print(a == b)  # True
print(a > c)   # True
print(b <= a)  # True
```

-   Supported operators: `==`, `!=`, `>`, `<`, `>=`, `<=`

### In-Place Operations

The standard in-place operators are supported. Since `Sexagesimal` objects are immutable, these operators return a new instance of the class.

```python
s = Sexagesimal("1;30")
print(f"Initial ID: {id(s)}")

s += Sexagesimal("0;30") # This reassigns 's' to a new object

print(f"Final Value: {s}")
print(f"Final ID:   {id(s)}")

# Initial ID: 130575982851472 (will different everytime)
# Final Value: 02;00
# Final ID:   130575982846288 (definitely different from above)
```

-   Supported operators: `+=`, `-=`, `*=`