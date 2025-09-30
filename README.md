# Sexagesimal Calculator

[![PyPI version](https://badge.fury.io/py/sexagesimal-calculator.svg)](https://badge.fury.io/py/sexagesimal-calculator)
![Python versions](https://img.shields.io/pypi/pyversions/sexagesimal-calculator)
[![Coverage Status](https://coveralls.io/repos/github/HrushikeshPawar/Sexagesimal-Calculator/badge.svg?branch=main)](https://coveralls.io/github/HrushikeshPawar/Sexagesimal-Calculator?branch=main)
[![Pepy Total Downloads](https://img.shields.io/pepy/dt/sexagesimal-calculator)](https://pepy.tech/project/sexagesimal-calculator)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![GitHub stars](https://img.shields.io/github/stars/HrushikeshPawar/sexagesimal-calculator?style=social)
![GitHub issues](https://img.shields.io/github/issues/HrushikeshPawar/sexagesimal-calculator)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A robust, modern Python library for high-precision sexagesimal (base-60) arithmetic, born from a project for the [History of Mathematics in India (HoMI)](https://sites.iitgn.ac.in/homi/) initiative at [Indian Institute of Technology, Gandhinagar](https://iitgn.ac.in/).

This library provides a `Sexagesimal` class that represents numbers as immutable objects, allowing for intuitive and accurate calculations. It is ideal for applications in historical mathematics, astronomy, and any domain requiring base-60 computation.

---

**[Full Documentation](https://hrushikeshpawar.github.io/Sexagesimal-Calculator/)** | **[PyPI Project](https://pypi.org/project/sexagesimal-calculator/)** | **[Source Code](https://github.com/HrushikeshPawar/Sexagesimal-Calculator)**

---

## Features

-   **Immutable Objects:** `Sexagesimal` numbers are immutable, ensuring predictable and bug-free calculations.
-   **Intuitive API:** Use standard Python operators (`+`, `-`, `*`, `/`, `**`, `round()`) for all arithmetic.
-   **High Precision:** Backed by Python's `Decimal` and `sympy.Rational` for conversions, guaranteeing precision.
-   **Flexible Initialization:** Create `Sexagesimal` numbers from integers, floats, decimals, or strings.
-   **Educational Tools:** Generate beautiful, step-by-step explanations of calculations, perfect for teaching or validation.
-   **Fully Typed and Tested:** High test coverage with a comprehensive `pytest` and `hypothesis` suite.

## Installation

This package is hosted on PyPI.

```bash
pip install sexagesimal-calculator

# OR

uv add sexagesimal-calculator
```

## Basic Usage

The core of the library is the `Sexagesimal` class.

```python
from sexagesimal_calculator import Sexagesimal

# Initialization is flexible
a = Sexagesimal("10;15,30") # From a sexagesimal string
b = Sexagesimal(1.75)       # From a float
c = Sexagesimal("-5")       # From an integer string

print(f"A = {a}") # A = 10;15,30
print(f"B = {b}") # B = 01;45
print(f"C = {c}") # C = -05;00

# Arithmetic uses standard Python operators
sum_val = a + b
print(f"A + B = {sum_val}") # A + B = 12;00,30

# Convert to a high-precision Decimal
dec_val = sum_val.to_decimal()
print(f"Sum as Decimal: {dec_val}") # Sum as Decimal: 12.008333...

# Rounding
rounded = Sexagesimal("21;19,53,47").round(precision=2)
print(f"Rounded value: {rounded}") # Rounded value: 21;19,54
```

## Explanations Feature

A standout feature is the ability to generate detailed, step-by-step explanations for calculations.

```python
from sexagesimal_calculator import explain_multiplication

a = Sexagesimal("01;15")
b = Sexagesimal("02;30")

# Generate the explanation object
explanation = explain_multiplication(a, b)

# Print the beautiful, colored explanation to your terminal
explanation.print()
```

This produces a detailed, formatted breakdown of the entire long multiplication process, perfect for educational purposes. Similar functions (`explain_addition`, `explain_subtraction`, `explain_division`) are also available.

## Development

To set up for development, clone the repository and use `uv` to sync dependencies.

```bash
git clone https://github.com/HrushikeshPawar/Sexagesimal-Calculator.git
cd Sexagesimal-Calculator
uv sync --all-packages
```

To run the test suite with coverage:
```bash
uv run pytest --cov=src/sexagesimal_calculator
```