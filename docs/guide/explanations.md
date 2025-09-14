# Educational Explanations

A unique feature of this library is its ability to generate detailed, step-by-step explanations of its calculations. This is perfect for educational settings, debugging, or simply understanding how sexagesimal arithmetic works.

### How to Use

For each major operation, there is a corresponding `explain_*` function.

```python
from sexagesimal_calculator import Sexagesimal, explain_multiplication

a = Sexagesimal("01;15")
b = Sexagesimal("02;30")

# 1. Generate the explanation object
explanation = explain_multiplication(a, b)

# 2. Print the beautiful, colored explanation to your terminal
explanation.print()
```

### Available Functions

- `explain_addition(a, b)`
- `explain_subtraction(a, b)`
- `explain_multiplication(a, b)`
- `explain_division(a, b)`

Each function returns a `VerboseResult` object, which you can print directly or convert to a plain string with `str()`.

---

### Advanced Usage with `rich`

The `VerboseResult` object returned by the `explain_*` functions has a special `__rich_console__` method. This means it is a native "renderable" for the [`rich`](https://rich.readthedocs.io/en/latest/introduction.html) library.

You can print the explanation using your own custom `rich.console.Console` to control the width, styling, or export the result.

```python
from rich.console import Console
from sexagesimal_calculator import Sexagesimal, explain_addition

# Create a custom console
my_console = Console(width=100, record=True)

a = Sexagesimal("59;30")
b = Sexagesimal("1;45")
explanation = explain_addition(a, b)

# The console knows how to render our object automatically
my_console.print(explanation)

# You can even save the output as HTML
my_console.save_html("explanation.html")
```
