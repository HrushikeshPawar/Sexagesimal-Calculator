# In demo.py

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# To run this script, your library must be installed in editable mode,
# or you must set the PYTHONPATH. The simplest way is to run:
# pip install -e .
# from the root of your project.
from sexagesimal_calculator import Sexagesimal
from sexagesimal_calculator.explain import (
    explain_addition,
    explain_subtraction,
    explain_multiplication,
    explain_division,
)


def main():
    """Runs a visual demonstration of all explain methods."""
    console = Console()

    title = Panel(
        Text("Sexagesimal Calculator - Explanation Demo", justify="center", style="bold yellow"),
        border_style="cyan",
        title="[bold]Welcome![/]",
        title_align="left",
    )
    console.print(title)
    console.print("This script demonstrates the verbose, step-by-step output for each arithmetic operation.\n")

    # --- Addition Cases ---
    console.print(Panel("[bold green]Addition Explanations[/]", border_style="green"))
    addition_cases = [
        ("Simple addition", "02;15", "03;30"),
        ("Addition with fractional carry", "01;45", "01;45"),
        ("Addition with integer carry", "59;30", "01;30"),
        (
            "Addition where signs differ (delegates to subtraction)",
            "10;00",
            "-05;30",
        ),
    ]
    for title, a_str, b_str in addition_cases:
        console.print(f"\n[bold underline]Case: {title}[/]")
        a, b = Sexagesimal(a_str), Sexagesimal(b_str)
        explain_addition(a, b).print()

    # --- Subtraction Cases ---
    console.print(Panel("[bold magenta]Subtraction Explanations[/]", border_style="magenta"))
    subtraction_cases = [
        ("Simple subtraction", "10;45", "05;15"),
        ("Subtraction with borrow", "10;15", "05;30"),
        (
            "Subtraction where result is negative",
            "05;00",
            "10;00",
        ),
        (
            "Subtraction where signs differ (delegates to addition)",
            "10;00",
            "-05;30",
        ),
        (
            "Subtracting two negative numbers (delegates to positive subtraction)",
            "-10;00",
            "-05;30",
        ),
    ]
    for title, a_str, b_str in subtraction_cases:
        console.print(f"\n[bold underline]Case: {title}[/]")
        a, b = Sexagesimal(a_str), Sexagesimal(b_str)
        explain_subtraction(a, b).print()

    # --- Multiplication Cases ---
    console.print(Panel("[bold yellow]Multiplication Explanations[/]", border_style="yellow"))
    multiplication_cases = [
        ("Simple multiplication", "10;00", "05;00"),
        ("Multiplication with fractional parts", "01;15", "02;30"),
    ]
    for title, a_str, b_str in multiplication_cases:
        console.print(f"\n[bold underline]Case: {title}[/]")
        a, b = Sexagesimal(a_str), Sexagesimal(b_str)
        explain_multiplication(a, b).print()

    # --- Division Cases ---
    console.print(Panel("[bold red]Division Explanations[/]", border_style="red"))
    division_cases = [
        ("Simple division (terminating)", "10;00", "04;00"),
        ("Division with non-terminating result", "10;00", "03;00"),
        ("Division by zero", "10;00", "0;00"),
    ]
    for title, a_str, b_str in division_cases:
        console.print(f"\n[bold underline]Case: {title}[/]")
        a, b = Sexagesimal(a_str), Sexagesimal(b_str)
        explain_division(a, b).print()


if __name__ == "__main__":
    main()
