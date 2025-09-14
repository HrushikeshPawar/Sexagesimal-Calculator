# Utility Functions

The library provides additional utility functions for more specialized tasks.

### `increment_table()`

This function generates a list of sexagesimal values, starting from an initial value and repeatedly adding an increment. It's useful for creating historical mathematical tables.

```python
from sexagesimal_calculator import increment_table

# Generate a table starting at 1;30 with an increment of 0;45 for 5 rows
table = increment_table(initial="1;30", increment="0;45", rows=5)

for value in table:
    print(value)
```

**Output:**
```bash
01;30
02;15
03;00
03;45
04;30
05;15
```

#### Modulo Behavior

The `mod` parameter can be used to wrap the integer part of the values around a certain number, which is common in astronomical tables.

```python
# Generate a table that wraps around at 60
table = increment_table(initial="58;00", increment="1;00", rows=3, mod=60)
print(table)
# ['58;00', '59;00', '00;00', '01;00']
```