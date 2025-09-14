## Project Overview

This project is a Python library for performing arithmetic operations on sexagesimal (base-60) numbers. It provides a `Sexagesimal` class that supports initialization from integers, floats, and strings, as well as addition, subtraction, multiplication, and division. All calculations are performed in the sexagesimal number system without converting to decimal in the background.

The main logic is implemented in the `src/sexagesimal_calculator/sexagesimal.py` file. The project uses `pytest` for testing, with tests located in the `test/` directory. The project is configured using `pyproject.toml` and has `sympy` as a dependency.

## Building and Running

### Installation

To install the package, run the following command:

```bash
uv sync
```

### Running Tests

To run the tests, first install the development dependencies:

```bash
uv sync --all-packages
```

Then run `pytest`:

```bash
uv run pytest
```

## Development Conventions

### Code Style and Linting

The code follows the standard Python conventions (PEP 8). This project uses `ruff` for linting and formatting. The pre-commit hooks are configured in `.pre-commit-config.yaml` to automatically format and lint the code before each commit.

### Testing

The project uses `pytest` for testing. All new functionality should be accompanied by corresponding tests. The tests are located in the `test/test_sexagesimal.py` file.

### Dependencies

The project uses `uv` to manage dependencies, which are listed in the `pyproject.toml` file. The `uv.lock` file is used to lock the dependencies. The pre-commit hooks are configured to automatically sync the dependencies.

### Commit Messages

This project follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. A pre-commit hook is configured to enforce this convention.
