from dataclasses import dataclass
from typing import List, Union

from io import StringIO
from rich.console import Console, ConsoleOptions, RenderResult
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from sexagesimal_calculator.sexagesimal import Sexagesimal
from sexagesimal_calculator.core import BASE
from sexagesimal_calculator.arithmetic import pad_parts, compare_magnitude
from sexagesimal_calculator.conversion import to_rational

# --------------------- Data Structures for Explanations --------------------- #


@dataclass(frozen=True)
class CalculationGrid:
    """Stores the raw data needed to render an arithmetic grid."""

    # This can now hold 2 rows for addition or N rows for multiplication
    body_rows: List[List[int]]
    result_row: List[int]
    operator: str
    max_len: int


# A container for a single line of explanation
@dataclass(frozen=True)
class ExplanationStep:
    """Represents one step or detail in the narrative."""

    description: str
    value: str = ""


# The main result object that will be returned to the user
@dataclass(frozen=True)
class VerboseResult:
    """A container for the final result and the rich explanation steps."""

    result: Sexagesimal
    title: str
    steps: List[Union[ExplanationStep, CalculationGrid]]

    def __str__(self) -> str:
        """Renders the explanation to a plain, uncolored string."""
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=False, width=80)
        console.print(self)
        return string_io.getvalue().strip()

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> "RenderResult":
        """Allows the object to be printed directly by a rich.console.Console."""
        header = f" {self.title} "
        yield Panel(Text(header, justify="center"), style="bold cyan", border_style="cyan")

        for item in self.steps:
            if isinstance(item, ExplanationStep):
                line = Text.from_markup(f"[green]•[/] {item.description}")
                if item.value:
                    line.append(f"\n{'': >8} -> {item.value}", style="dim")
                yield line
            elif isinstance(item, CalculationGrid):
                yield self._render_grid(item)

        yield Text.from_markup(f"\n[bold green]Final Result:[/] [bold yellow]{self.result}[/]")

    def print(self):
        """Prints the rich, colored explanation directly to the console."""
        console = Console()
        console.print(self)

    def _render_grid(self, grid: CalculationGrid) -> Table:
        """Helper to render an arithmetic grid using rich."""
        table = Table(show_header=False, show_lines=False, border_style="dim blue", box=None, padding=1)
        # Add a column for the operator
        table.add_column(justify="right")
        num_body_rows = len(grid.body_rows)
        for i, row_data in enumerate(grid.body_rows):
            # Pad each row to the max length
            padded_row = [""] * (grid.max_len - len(row_data)) + [f"{d:0>2}" for d in row_data]

            # Place the operator next to the LAST body row
            operator_symbol = f"[bold]{grid.operator}[/]" if i == num_body_rows - 1 else ""
            table.add_row(operator_symbol, *padded_row)

        table.add_section()
        result_row = [""] * (grid.max_len - len(grid.result_row)) + [f"{d:0>2}" for d in grid.result_row]
        table.add_row("", *result_row, style="bold yellow")

        return table


# --------------------------- Explanation Functions -------------------------- #


def explain_multiplication(a: Sexagesimal, b: Sexagesimal) -> VerboseResult:
    """
    Explain long multiplication of two sexagesimal values and produce a verbose narrative.

    Summary:
        Perform a pedagogical, step-by-step long multiplication of two Sexagesimal
        instances. The explanation breaks each operand into integer and fractional
        base-60 digits, computes intermediate row products (digit-by-digit with carries),
        arranges a summation grid with proper shifts, reduces the accumulated digits
        into integer and fractional parts, and reports the canonical normalized result.

    Args:
        a (Sexagesimal): Left multiplicand.
        b (Sexagesimal): Right multiplicand.

    Returns:
        VerboseResult: A container with the canonical Sexagesimal product in `result`,
            a short `title`, and a `steps` list combining ExplanationStep entries and
            a CalculationGrid showing intermediate rows and the final column-wise sum.

    Notes:
        - The narrative includes decomposition, per-digit multiplication (with carry),
          the shifted intermediate rows, column-wise summation and carry propagation,
          splitting the full digit array into integer/fractional parts, and final normalization.
        - The function uses the robust Sexagesimal.__mul__ implementation to produce
          the authoritative final result after demonstrating the manual algorithm.
    """
    title = f"Long Multiplication of {a} * {b}"
    steps: List[Union[ExplanationStep, CalculationGrid]] = []

    steps.append(ExplanationStep(f"Inputs: A = {a}, B = {b}"))

    # --- Step 1: Breakdown ---
    steps.append(ExplanationStep("Break down numbers into their integer and fractional parts:"))
    steps.append(ExplanationStep(f"  - A (int): {a.integer_part}, A (frac): {a.fractional_part}"))
    steps.append(ExplanationStep(f"  - B (int): {b.integer_part}, B (frac): {b.fractional_part}"))

    a_full = list(a.integer_part + a.fractional_part)
    b_full = list(b.integer_part + b.fractional_part)
    steps.append(ExplanationStep("Combine parts into full digit arrays for calculation:"))
    steps.append(ExplanationStep(f"  - A_full = {a_full}"))
    steps.append(ExplanationStep(f"  - B_full = {b_full}"))

    # --- Step 2 & 3: Digit-by-Digit Multiplication ---
    steps.append(
        ExplanationStep("\nPerform multiplication for each digit of B against all digits of A (right to left):")
    )

    intermediate_rows = []
    for i, b_digit in enumerate(reversed(b_full)):
        steps.append(ExplanationStep(f"  Multiplying A_full by B's digit '{b_digit}' (position {i}):"))

        intermediate_product = []
        carry = 0
        for a_digit in reversed(a_full):
            prod = (a_digit * b_digit) + carry
            steps.append(
                ExplanationStep(
                    f"    - Calculation: ({b_digit:0>2} * {a_digit:0>2}) + {carry: >2} = {prod: >3}  ->  Digit: {prod % BASE: >2}, Carry: {prod // BASE: >2}"
                )
            )
            intermediate_product.insert(0, prod % BASE)
            carry = prod // BASE
        if carry > 0:
            intermediate_product.insert(0, carry)

        steps.append(ExplanationStep(f"  --> Intermediate Product: {intermediate_product}"))
        intermediate_rows.append(intermediate_product)

    # --- Step 4 & 5: The Grid and Summation ---
    steps.append(ExplanationStep("\nArrange intermediate products, shifting each row left, and sum columns:"))

    # Prepare data for the CalculationGrid
    shifted_rows_for_sum = [row + [0] * i for i, row in enumerate(intermediate_rows)]
    max_len = max(len(row) for row in shifted_rows_for_sum) if shifted_rows_for_sum else 0

    final_result_digits = []
    carry = 0
    for i in range(max_len):
        col_sum = carry
        for row in shifted_rows_for_sum:
            # Get digit from the right end of the row
            if i < len(row):
                col_sum += row[-(i + 1)]

        final_result_digits.insert(0, col_sum % BASE)
        carry = col_sum // BASE
    if carry > 0:
        final_result_digits.insert(0, carry)

    # Add the grid object to our steps
    grid = CalculationGrid(
        body_rows=shifted_rows_for_sum, result_row=final_result_digits, operator="*", max_len=len(final_result_digits)
    )
    steps.append(grid)

    # --- Step 6, 7, 8: Splitting, Normalizing, and Signing ---
    total_frac_places = len(a.fractional_part) + len(b.fractional_part)
    steps.append(
        ExplanationStep(
            f"\nTotal fractional places in result is the sum of operand fractional places: {total_frac_places}"
        )
    )

    split_point = len(final_result_digits) - total_frac_places
    int_part = final_result_digits[:split_point] or [0]
    frac_part = final_result_digits[split_point:]
    steps.append(
        ExplanationStep(
            f"Split the result array at position -{total_frac_places} -> Int: {int_part}, Frac: {frac_part}"
        )
    )

    # IMPORTANT: The final result comes from the robust __mul__ method to ensure correctness.
    final_result = a * b
    steps.append(ExplanationStep("Normalize the parts and apply the final sign to get the canonical result."))

    return VerboseResult(result=final_result, title=title, steps=steps)


def explain_addition(a: Sexagesimal, b: Sexagesimal) -> VerboseResult:
    """
    Explain addition of two sexagesimal values and produce a verbose narrative.

    Summary:
        Produce a step-by-step, pedagogical explanation of adding two Sexagesimal
        instances. The explanation documents sign handling (delegating to subtraction
        for mixed signs), alignment of integer and fractional digits, per-column
        addition with carry propagation from fractional to integer places, construction
        of a calculation grid showing the aligned operands and result, and the final
        canonical, normalized sum.

    Args:
        a (Sexagesimal): Left addend.
        b (Sexagesimal): Right addend.

    Returns:
        VerboseResult: A container holding:
            - result (Sexagesimal): the canonical sum (produced by the library's
              arithmetic to guarantee normalization),
            - title (str): a short descriptive title,
            - steps (List[Union[ExplanationStep, CalculationGrid]]): a sequence of
              narrative steps and a CalculationGrid illustrating the work.

    Notes:
        - When operands have opposite signs the narrative records the transformation
          (e.g. A + (-B) -> A - B) and delegates to explain_subtraction to show the
          borrowing behavior; the combined explanation is returned.
        - Fractional parts are right-padded and integer parts are left-padded for
          alignment prior to column-wise processing. Carries from fractional addition
          propagate into integer columns and may produce a new high-order digit.
        - The function both demonstrates the manual algorithm (for teaching) and
          uses the authoritative Sexagesimal addition (a + b) to produce the final,
          normalized result included in the VerboseResult.
    """

    title = f"Addition of {a} + {b}"

    # Handle sign logic by delegating to subtraction if signs differ
    if a.is_negative != b.is_negative:
        steps = [
            ExplanationStep("Signs of the operands are different."),
            ExplanationStep("The operation delegates to subtraction to handle the mixed signs."),
        ]
        if a.is_negative:
            # -A + B  ->  B - A
            steps.append(ExplanationStep("Operation becomes: B - A", f"{b} - {abs(a)}"))
            sub_explanation = explain_subtraction(b, abs(a))
        else:
            # A + -B  ->  A - B
            steps.append(ExplanationStep("Operation becomes: A - B", f"{a} - {abs(b)}"))
            sub_explanation = explain_subtraction(a, abs(b))

        # Prepend our explanation to the steps from the subtraction explanation
        return VerboseResult(result=sub_explanation.result, title=title, steps=steps + sub_explanation.steps)

    steps: List[Union[ExplanationStep, CalculationGrid]] = []

    steps.append(ExplanationStep("Both numbers have the same sign, so we add their magnitudes and keep the sign."))

    # Pad fractional parts
    frac_a, frac_b = pad_parts(a.fractional_part, b.fractional_part, pad_left=False)
    # Add integer parts
    int_a, int_b = pad_parts(a.integer_part, b.integer_part, pad_left=True)

    steps.append(ExplanationStep("Align integer and fractional parts by padding with zeros."))

    # Narrate fractional addition
    steps.append(ExplanationStep("Add fractional parts from right to left, carrying over values >= BASE."))
    frac_res, carry = [], 0
    for d1, d2 in zip(reversed(frac_a), reversed(frac_b)):
        total = d1 + d2 + carry
        digit = total % BASE
        carry = total // BASE
        frac_res.insert(0, digit)
        steps.append(
            ExplanationStep(
                f"  - Column: ({d1:0>2} + {d2:0>2}) + carry {carry} = {total}", f"Digit: {digit}, New Carry: {carry}"
            )
        )

    steps.append(ExplanationStep(f"Final carry from fractional part: {carry}"))

    # Narrate integer addition
    steps.append(ExplanationStep("Add integer parts from right to left, including final fractional carry."))
    int_res = []
    for d1, d2 in zip(reversed(int_a), reversed(int_b)):
        total = d1 + d2 + carry
        digit = total % BASE
        carry = total // BASE
        int_res.insert(0, digit)
        steps.append(
            ExplanationStep(
                f"  - Column: ({d1:0>2} + {d2:0>2}) + carry {carry} = {total}", f"Digit: {digit}, New Carry: {carry}"
            )
        )

    if carry > 0:
        int_res.insert(0, carry)
        steps.append(ExplanationStep(f"Final carry creates a new high-order digit: {carry}"))

    grid = CalculationGrid(
        body_rows=[list(int_a + frac_a), list(int_b + frac_b)],
        result_row=int_res + frac_res,
        operator="+",
        max_len=len(int_res + frac_res),
    )
    steps.append(grid)

    final_result = a + b
    return VerboseResult(result=final_result, title=title, steps=steps)


def explain_subtraction(a: Sexagesimal, b: Sexagesimal) -> VerboseResult:
    """
    Explain subtraction of two sexagesimal values and produce a verbose narrative.

    Summary:
        Produce a pedagogical, step-by-step explanation of computing A - B for
        Sexagesimal operands. The explanation documents sign handling (delegating
        to addition when signs differ), magnitude comparison, the borrow algorithm
        across fractional and integer base-60 places, construction of a calculation
        grid showing aligned operands and the result, and the canonical normalized
        final value.

    Args:
        a (Sexagesimal): Minuend.
        b (Sexagesimal): Subtrahend.

    Returns:
        VerboseResult: A container with:
            - result (Sexagesimal): canonical difference (produced by the library's
              arithmetic to guarantee normalization),
            - title (str): a short descriptive title,
            - steps (List[Union[ExplanationStep, CalculationGrid]]): narrative steps
              and a CalculationGrid illustrating the borrowing and column-wise work.

    Notes:
        - When operands have opposite signs the function records the transformation
          (e.g. -A - +B -> -(A + B), +A - -B -> A + B) and delegates to the addition
          explainer; the returned VerboseResult combines both narratives and the
          correctly signed final result.
        - For magnitude subtraction the algorithm pads fractional parts on the right
          and integer parts on the left for alignment, subtracts right-to-left,
          propagating borrows from fractional into integer places as necessary.
        - The calculation grid shows the padded operand rows and the raw digitwise
          result; the authoritative final Sexagesimal value is produced by the
          library subtraction (a - b) to ensure normalization and canonical zero/sign.
    """

    title = f"Subtraction of {a} - {b}"

    # Handle sign logic by delegating to addition
    if a.is_negative != b.is_negative:
        steps = [
            ExplanationStep("Signs of the operands are different."),
            ExplanationStep("The operation delegates to addition to handle the mixed signs."),
        ]
        if a.is_negative:
            # -A - +B  ->  -(A + B)
            steps.append(ExplanationStep("Operation becomes: -(A + B)", f"-({abs(a)} + {b})"))
            add_explanation = explain_addition(abs(a), b)

            # Prepend steps and negate the final result
            return VerboseResult(
                result=-(add_explanation.result),  # Correctly negates the final result
                title=title,
                steps=steps + add_explanation.steps,
            )
        else:
            # +A - -B  ->  A + B
            steps.append(ExplanationStep("Operation becomes: A + B", f"{a} + {abs(b)}"))
            add_explanation = explain_addition(a, abs(b))

            return VerboseResult(result=add_explanation.result, title=title, steps=steps + add_explanation.steps)

    # If both negative, swap to a positive subtraction
    if a.is_negative and b.is_negative:
        steps = [ExplanationStep("Both numbers are negative.")]
        steps.append(ExplanationStep("Operation -A - -B is equivalent to B - A", f"{abs(b)} - {abs(a)}"))
        sub_explanation = explain_subtraction(abs(b), abs(a))

        return VerboseResult(result=sub_explanation.result, title=title, steps=steps + sub_explanation.steps)

    # --- Core Magnitude Subtraction ---
    steps: List[Union[ExplanationStep, CalculationGrid]] = []

    comparison = compare_magnitude(a._parts, b._parts)
    steps.append(ExplanationStep("Both numbers are positive. First, compare their magnitudes."))

    if comparison == 0:
        steps.append(ExplanationStep("Magnitudes are equal, so the result is zero.", f"{a} - {b} = 0"))
        return VerboseResult(result=Sexagesimal(0), title=title, steps=steps)

    elif comparison > 0:
        steps.append(ExplanationStep("A is larger than B, so the result will be positive."))
        larger, smaller = a, b
    else:  # comparison < 0
        steps.append(
            ExplanationStep(
                "B is larger than A, so the result will be negative. We will calculate B - A and negate the result."
            )
        )
        larger, smaller = b, a

    # ... (Narrate the borrowing algorithm, similar to addition) ...
    frac_l, frac_s = pad_parts(larger.fractional_part, smaller.fractional_part, pad_left=False)
    int_l, int_s = pad_parts(larger.integer_part, smaller.integer_part, pad_left=True)

    steps.append(ExplanationStep("Subtract fractional parts from right to left, borrowing from the left when needed."))
    frac_res, borrow = [], 0
    for d1, d2 in zip(reversed(frac_l), reversed(frac_s)):
        val = d1 - d2 - borrow
        if val < 0:
            digit, new_borrow = val + BASE, 1
        else:
            digit, new_borrow = val, 0
        frac_res.insert(0, digit)
        steps.append(
            ExplanationStep(
                f"  - Column: ({d1:0>2} - {d2:0>2}) - borrow {borrow} = {val}",
                f"Digit: {digit}, New Borrow: {new_borrow}",
            )
        )
        borrow = new_borrow

    steps.append(ExplanationStep(f"Final borrow from fractional part: {borrow}"))

    steps.append(ExplanationStep("Subtract integer parts, including final fractional borrow."))
    int_res = []
    for d1, d2 in zip(reversed(int_l), reversed(int_s)):
        val = d1 - d2 - borrow
        if val < 0:
            digit, new_borrow = val + BASE, 1
        else:
            digit, new_borrow = val, 0
        int_res.insert(0, digit)
        steps.append(
            ExplanationStep(
                f"  - Column: ({d1:0>2} - {d2:0>2}) - borrow {borrow} = {val}",
                f"Digit: {digit}, New Borrow: {new_borrow}",
            )
        )
        borrow = new_borrow

    grid = CalculationGrid(
        body_rows=[list(int_l + frac_l), list(int_s + frac_s)],
        result_row=int_res + frac_res,
        operator="-",
        max_len=len(int_res + frac_res),
    )
    steps.append(grid)

    final_result = a - b
    return VerboseResult(result=final_result, title=title, steps=steps)


def explain_division(a: Sexagesimal, b: Sexagesimal) -> VerboseResult:
    """
    Explain division of two sexagesimal values using exact rational arithmetic.

    Summary:
        Demonstrate a clear, step-by-step strategy for dividing two Sexagesimal
        instances by converting them to exact Rational numbers, performing the
        division exactly, and then converting the quotient back into a sexagesimal
        expansion (showing a limited number of fractional-place extraction steps
        for pedagogy). The function also documents the handling of division by
        zero and presents a human-friendly narrative describing the conversion
        and extraction process.

    Args:
        a (Sexagesimal): Numerator.
        b (Sexagesimal): Denominator.

    Returns:
        VerboseResult: A container with:
            - result (Sexagesimal): the canonical quotient (produced by the
              library's division to ensure normalization and correct sign),
            - title (str): a short descriptive title,
            - steps (List[ExplanationStep]): a sequence of narrative steps that
              explain conversion to Rational, the exact division, and the process
              of recovering sexagesimal integer and fractional digits.

    Notes:
        - Division is performed via exact Rational arithmetic (to avoid rounding
          errors). The sexagesimal expansion of the quotient may be terminating
          or repeating; the explainer shows the first few fractional extraction
          steps (for demonstration) while the authoritative final Sexagesimal
          result is obtained from the library's division operator.
        - If the denominator is zero the function records an error step and
          returns a placeholder VerboseResult (no numeric result can be produced).
        - The conversion back to sexagesimal is performed by extracting the
          integer part and repeatedly multiplying the fractional remainder by
          BASE (60) to obtain successive base-60 digits; this process is shown
          only up to a short demonstration depth in the narrative.
    """
    title = f"Division of {a} / {b}"
    steps: List[ExplanationStep] = []

    if b == Sexagesimal(0):
        steps.append(ExplanationStep("Error: Cannot divide by zero.", "This operation is undefined."))
        # We can't calculate a result, so we pass a placeholder.
        return VerboseResult(result=Sexagesimal("0;0"), title=title, steps=steps)  # type: ignore

    steps.append(ExplanationStep("The most precise method for division is to use exact fractions (Rational numbers)."))

    # Step 1 & 2: Convert to Rational
    a_rat = to_rational(a)
    b_rat = to_rational(b)
    steps.append(ExplanationStep("Convert the numerator (A) to a rational number.", f"{a} -> {a_rat}"))
    steps.append(ExplanationStep("Convert the denominator (B) to a rational number.", f"{b} -> {b_rat}"))

    # Step 3: Divide
    res_rat = a_rat / b_rat  # type: ignore
    steps.append(ExplanationStep("Divide the two rational numbers.", f"({a_rat}) / ({b_rat}) = {res_rat}"))

    # Step 4: Convert back
    steps.append(
        ExplanationStep("\nConvert the resulting rational number back to sexagesimal (up to 80 fractional places).")
    )

    integer_part = int(abs(res_rat))
    remainder = abs(res_rat) - integer_part
    steps.append(ExplanationStep("Extract the integer part of the result.", f"int({abs(res_rat)}) = {integer_part}"))
    steps.append(
        ExplanationStep(
            "The remaining fractional part is a new rational.", f"{abs(res_rat)} - {integer_part} = {remainder}"
        )
    )

    steps.append(ExplanationStep("Find fractional digits by repeatedly multiplying the remainder by BASE:"))
    for i in range(5):  # Show first 5 steps
        if remainder == 0:
            steps.append(ExplanationStep(f"  - Step {i + 1}: Remainder is 0. The fraction terminates.", ""))
            break

        new_val = remainder * BASE
        digit = int(new_val)
        remainder = new_val - digit
        steps.append(
            ExplanationStep(
                f"  - Step {i + 1}: remainder * BASE = {new_val}", f"Digit: {digit}, New Remainder: {remainder}"
            )
        )
    else:
        steps.append(ExplanationStep("  - (This process continues up to the precision limit...)"))

    final_result = a / b
    return VerboseResult(result=final_result, title=title, steps=steps)  # type: ignore
