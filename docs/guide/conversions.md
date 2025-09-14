# Conversions & Rounding

### Converting to Decimal (`.to_decimal()`)

You can convert any `Sexagesimal` number to a high-precision Python `Decimal` object using the `.to_decimal()` method. This is the recommended way to get a decimal value, as it avoids the inaccuracies of standard floats.

The method takes an optional `precision` argument that controls the number of significant digits for the calculation.

```python
s = Sexagesimal("21;19,53,47")

# Default precision
print(s.to_decimal())
# 21.331606481481481481481481481481481481481481481482

# Higher precision
print(s.to_decimal(precision=60))
# 21.3316064814814814814814814814814814814814814814814814814815
```

### Rounding

The `.round()` method allows you to round a `Sexagesimal` number to a specific number of fractional places. It uses "round half up" logic (values >= 30 are rounded up).

```python
s = Sexagesimal("10;14,30")
rounded = s.round(precision=1)
print(rounded)
# 10;15

# Rounding can cascade carries
s2 = Sexagesimal("59;59,30")
rounded2 = s2.round(precision=0) # Round to nearest integer
print(rounded2)
# 01,00;00
```