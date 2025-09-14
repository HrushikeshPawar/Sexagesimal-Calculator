# Welcome to the Sexagesimal Calculator

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

### Features

-   **Immutable Objects:** `Sexagesimal` numbers are immutable, ensuring predictable and bug-free calculations.
-   **Intuitive API:** Use standard Python operators (`+`, `-`, `*`, `/`, `**`, `round()`) for all arithmetic.
-   **High Precision:** Backed by Python's `Decimal` and `sympy.Rational` for conversions, guaranteeing precision.
-   **Educational Tools:** Generate beautiful, step-by-step explanations of calculations, perfect for teaching or validation.
-   **Fully Typed and Tested:** High test coverage with a comprehensive `pytest` and `hypothesis` suite.

Ready to get started? Check out the [**User Guide**](./guide/installation.md).