from typing import List, Tuple
from sexagesimal_calculator.core import SexagesimalParts, BASE
from sexagesimal_calculator.conversion import normalize_parts


def pad_parts(
    parts_A: Tuple[int, ...], parts_B: Tuple[int, ...], pad_left: bool = True
) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """
    Pad two sexagesimal-part tuples so they have equal length.

    Summary:
        Return two new tuples obtained by padding the shorter of the two inputs
        with zero-valued digits so both tuples share the same length. When
        pad_left is True zeros are added to the left (most-significant side),
        which is appropriate for integer-part alignment. When pad_left is False
        zeros are added to the right (least-significant side), which is
        appropriate for fractional-part alignment.

    Args:
        parts_A (Tuple[int, ...]): First sequence of base-60 digits (most-significant first).
        parts_B (Tuple[int, ...]): Second sequence of base-60 digits (most-significant first).
        pad_left (bool, optional): If True pad on the left (MSB side). If False pad on the
            right (LSB side). Defaults to True.

    Returns:
        Tuple[Tuple[int, ...], Tuple[int, ...]]: A pair (padded_A, padded_B) where both
        tuples have equal length and original ordering of digits is preserved.

    Notes:
        - This function does not mutate the input tuples; it returns new tuples.
        - It is used by arithmetic helpers to align integer and fractional parts
            prior to digit-wise addition, subtraction and comparison.
    """
    max_len = max(len(parts_A), len(parts_B))
    if pad_left:
        padded_A = (0,) * (max_len - len(parts_A)) + parts_A
        padded_B = (0,) * (max_len - len(parts_B)) + parts_B
    else:
        padded_A = parts_A + (0,) * (max_len - len(parts_A))
        padded_B = parts_B + (0,) * (max_len - len(parts_B))

    return padded_A, padded_B


def compare_magnitude(parts_a: SexagesimalParts, parts_b: SexagesimalParts) -> int:
    """
    Compare the magnitudes (absolute values) of two sexagesimal parts.

    Summary:
        Determine which of two normalized SexagesimalParts has the greater magnitude
        by performing the following checks in order:
          1. Compare the lengths of the integer-part tuples (more digits => larger magnitude).
          2. If lengths are equal, compare integer parts lexicographically.
          3. If integer parts are equal, right-pad fractional parts with zeros to equal
             length and compare them lexicographically.

    Args:
        parts_a (SexagesimalParts): First normalized parts to compare.
        parts_b (SexagesimalParts): Second normalized parts to compare.

    Returns:
        int:
             1   if |parts_a| > |parts_b|
            -1   if |parts_a| < |parts_b|
             0   if |parts_a| == |parts_b|

    Notes:
        - Inputs are expected to be normalized (no leading integer zeros or trailing fractional zeros).
        - Fractional parts are padded on the right (least-significant side) before comparison.
        - This function compares magnitude only; sign handling is the caller's responsibility.
    """
    # Compare integer parts length
    if len(parts_a.integer_part) != len(parts_b.integer_part):
        return 1 if len(parts_a.integer_part) > len(parts_b.integer_part) else -1

    # Compare integer parts lexicographically
    if parts_a.integer_part != parts_b.integer_part:
        return 1 if parts_a.integer_part > parts_b.integer_part else -1

    # Pad fractional parts with zeros to equal length
    self_frac, other_frac = pad_parts(parts_a.fractional_part, parts_b.fractional_part, pad_left=False)

    if self_frac != other_frac:
        return 1 if self_frac > other_frac else -1

    return 0  # They are equal


def subtract_magnitude(larger_parts: SexagesimalParts, smaller_parts: SexagesimalParts) -> SexagesimalParts:
    """
    Subtract the magnitude of two sexagesimal parts (assumes |larger| >= |smaller|).

    Summary:
        Perform a base-60 digit-wise subtraction of `smaller_parts` from `larger_parts`.
        The algorithm:
            - right-pads fractional parts to equal length and subtracts from least-significant
            fractional digit to most-significant, propagating borrows as needed;
            - left-pads integer parts to equal length and subtracts with any remaining borrow;
            - returns a normalized, immutable SexagesimalParts with a non-negative sign
            (caller is responsible for assigning the correct sign if needed).

    Args:
        larger_parts (SexagesimalParts): Normalized parts representing the minuend; must
            have magnitude greater than or equal to `smaller_parts`.
        smaller_parts (SexagesimalParts): Normalized parts representing the subtrahend.

    Returns:
        SexagesimalParts: A normalized, immutable parts container for the difference.
            The returned `is_negative` is always False (magnitude subtraction only).

    Notes:
        - Inputs are expected to be normalized (no leading integer zeros or trailing fractional zeros).
        - Fractional parts are padded on the right (LSB side); integer parts are padded on the left (MSB side).
        - Borrow propagation may affect multiple fractional and integer places.
    """

    # Pad fractional parts with zeros to equal length
    larger_frac, smaller_frac = pad_parts(larger_parts.fractional_part, smaller_parts.fractional_part, pad_left=False)

    # List for mutability
    larger_frac = list(larger_frac)
    smaller_frac = list(smaller_frac)

    result_frac_list: List[int] = []
    borrow: int = 0

    # Subtract fractional parts with borrow
    for a, b in zip(reversed(larger_frac), reversed(smaller_frac)):
        val = a - b - borrow
        if val < 0:
            val += BASE
            borrow = 1
        else:
            borrow = 0

        result_frac_list.insert(0, val)

    # Pad integer parts with zeros to equal length
    larger_int, smaller_int = pad_parts(larger_parts.integer_part, smaller_parts.integer_part, pad_left=True)
    larger_int = list(larger_int)
    smaller_int = list(smaller_int)

    result_int_list: List[int] = []
    # Subtract integer parts with borrow
    for a, b in zip(reversed(larger_int), reversed(smaller_int)):
        val = a - b - borrow
        if val < 0:
            val += BASE
            borrow = 1
        else:
            borrow = 0

        result_int_list.insert(0, val)

    # Return the normalized parts
    return normalize_parts(result_int_list, result_frac_list, False)


def add_magnitude(a_parts: List[int], b_parts: List[int]) -> List[int]:
    """
    Add two sequences of base-60 digits and return the summed digit list.

    Summary:
        Perform digit-wise addition of two lists representing contiguous base-60
        digits (most-significant first). The shorter input is left-padded with
        zeros for alignment, addition proceeds from least-significant to
        most-significant with carry propagation, and any final carry is expanded
        into additional high-order digits.

    Args:
        a_parts (List[int]): First sequence of base-60 digits (MSB first).
        b_parts (List[int]): Second sequence of base-60 digits (MSB first).

    Returns:
        List[int]: Resulting sequence of base-60 digits (MSB first). The result
            may be longer than either input if carries produce new high-order digits.

    Notes:
        - Inputs are treated immutably; this function builds and returns new lists.
        - Designed for internal use when adding combined integer+fractional digit arrays.
    """

    # Ensure both lists are of equal length
    length_diff = len(a_parts) - len(b_parts)
    if length_diff > 0:
        b_parts = [0] * length_diff + b_parts
    elif length_diff < 0:
        a_parts = [0] * (-length_diff) + a_parts

    result: List[int] = []
    carry: int = 0

    for a, b in zip(reversed(a_parts), reversed(b_parts)):
        total = a + b + carry
        result.insert(0, total % BASE)
        carry = total // BASE

    if carry > 0:
        while carry >= BASE:
            result.insert(0, carry % BASE)
            carry //= BASE
        result.insert(0, carry)

    return result


def multiply_parts(a_parts: SexagesimalParts, b_parts: SexagesimalParts) -> SexagesimalParts:
    """
    Multiply two normalized sexagesimal parts using long multiplication.

    Summary:
        Perform long multiplication treating the concatenated integer+fractional
        digit sequences of each operand as contiguous base-60 digits (MSB first).
        - Combine integer and fractional parts into full digit arrays.
        - Multiply a_full by each digit of b_full (right-to-left), producing
            intermediate products with appropriate shifts.
        - Accumulate intermediate products using add_magnitude.
        - Re-split the accumulated result into integer and fractional parts
            according to the total fractional place count.
        - Normalize the result and set the sign to the XOR of the input signs.

    Args:
        a_parts (SexagesimalParts): Normalized parts of multiplicand.
        b_parts (SexagesimalParts): Normalized parts of multiplier.

    Returns:
        SexagesimalParts: Normalized parts for the product. Fractional length
        equals sum of input fractional lengths; returned parts are normalized
        (no extraneous leading/trailing zeros) and is_negative reflects the
        XOR of the input signs.

    Notes:
        - Inputs are expected normalized (no leading integer zeros, no trailing fractional zeros).
        - Uses BASE (60) arithmetic and the helper add_magnitude for accumulation.
        - Intermediate carries may increase the length of the result; final
            normalization ensures canonical representation.
    """

    # Step 1: Combine integer and fractional parts into single lists
    a_full = list(a_parts.integer_part) + list(a_parts.fractional_part)
    b_full = list(b_parts.integer_part) + list(b_parts.fractional_part)

    # Step 2: Total number of fractional places in the result
    total_frac_places = len(a_parts.fractional_part) + len(b_parts.fractional_part)

    # ------------------------ Perform Long Multiplication ----------------------- #
    # We will accumulate results of multiplying `a_full` by each digit of `b_full`
    result_full = []

    # Step 3: Iterate over each digit in b_full from right to left
    for idx, b_digit in enumerate(reversed(b_full)):
        intermediate_product: List[int] = []
        carry: int = 0

        # Step 3a: Multiply a_full by the current digit of b_full
        for a_digit in reversed(a_full):
            product = a_digit * b_digit + carry
            intermediate_product.insert(0, product % BASE)
            carry = product // BASE

        # Step 3b: Handle any remaining carry
        if carry > 0:
            while carry >= BASE:
                intermediate_product.insert(0, carry % BASE)
                carry //= BASE
            intermediate_product.insert(0, carry)

        # Step 3c: Shift the intermediate product according to its position
        # This is equivalent to multiplying by BASE**idx
        # We can achieve this by appending `idx` zeros at the end
        shifted_intermediate_product: List[int] = intermediate_product + [0] * idx

        # Step 3d: Add the shifted intermediate product to our running total
        result_full = add_magnitude(result_full, shifted_intermediate_product)

    # Step 4: Split the result into integer and fractional parts
    if total_frac_places > 0:
        int_part = result_full[:-total_frac_places] if len(result_full) > total_frac_places else [0]
        frac_part = result_full[-total_frac_places:]

    else:
        int_part = result_full
        frac_part = [0]

    # Step 5: Normalize and return the result parts
    return normalize_parts(int_part, frac_part, a_parts.is_negative ^ b_parts.is_negative)


def add(a_parts: SexagesimalParts, b_parts: SexagesimalParts) -> SexagesimalParts:
    """
    Add two normalized sexagesimal parts (magnitude addition in base-60).

    Summary:
        Compute the sum of two normalized SexagesimalParts by aligning their
        fractional and integer digit sequences, performing digit-wise addition
        in base BASE (60), and propagating carries from the least-significant
        fractional place up through integer places. Any final carry that
        extends the integer part is expanded into additional high-order digits.
        The returned parts are normalized and immutable.

    Args:
        a_parts (SexagesimalParts): Left addend; expected to be normalized
            (no extraneous leading integer zeros or trailing fractional zeros,
            except canonical zero).
        b_parts (SexagesimalParts): Right addend; same normalization expectation
            as `a_parts`.

    Returns:
        SexagesimalParts: A normalized, immutable parts container representing
        the sum. The returned `is_negative` flag is set to a_parts.is_negative
        (this function performs magnitude addition; callers should arrange sign
        semantics before calling).

    Notes:
        - Fractional parts are padded on the right (LSB side) for alignment.
        - Integer parts are padded on the left (MSB side) for alignment.
        - Inputs are treated immutably; this function builds and returns new lists.
        - This helper implements magnitude addition; sign-aware addition (mixing
          positives and negatives) is handled by the higher-level API.
    """

    # Step 1: Pad fractional parts with zeros to equal length
    self_frac, other_frac = pad_parts(a_parts.fractional_part, b_parts.fractional_part, pad_left=False)

    # Step 2: Add fractional parts with carry
    frac_result: List[int] = []
    carry: int = 0
    for a, b in zip(reversed(self_frac), reversed(other_frac)):
        total: int = a + b + carry
        frac_result.insert(0, total % BASE)
        carry: int = total // BASE

    # Step 3: Pad integer parts with zeros to equal length
    self_int, other_int = pad_parts(a_parts.integer_part, b_parts.integer_part, pad_left=True)

    # Step 4: Add integer parts with carry
    int_result: List[int] = []
    for a, b in zip(reversed(self_int), reversed(other_int)):
        total: int = a + b + carry
        int_result.insert(0, total % BASE)
        carry: int = total // BASE

    # Step 5: Handle any remaining carry
    if carry > 0:
        # Handle the final carry that extends the integer part
        # Carry >= 60
        while carry >= BASE:
            int_result.insert(0, carry % BASE)
            carry //= BASE
        int_result.insert(0, carry)

    # Step 6: Normalize and create new instance
    return normalize_parts(int_result, frac_result, a_parts.is_negative)


def subtract(a_parts: SexagesimalParts, b_parts: SexagesimalParts) -> SexagesimalParts:
    """
    Subtract two normalized sexagesimal parts (compute a_parts - b_parts).

    Summary:
        Perform sign-aware subtraction of two normalized SexagesimalParts.
        The function compares magnitudes and delegates to subtract_magnitude
        to compute the absolute-difference. The returned parts carry the
        appropriate sign:
          - If |a_parts| >= |b_parts| the result has the same sign as a_parts (usually non-negative).
          - If |a_parts| <  |b_parts| the result is the negation of the magnitude difference.

    Args:
        a_parts (SexagesimalParts): Minuend parts (normalized: no leading integer zeros or trailing fractional zeros).
        b_parts (SexagesimalParts): Subtrahend parts (same normalization expectation).

    Returns:
        SexagesimalParts: A normalized, immutable parts container representing a_parts - b_parts.
            The is_negative flag reflects the correct sign of the result; canonical zero is non-negative.

    Notes:
        - Inputs are expected to be normalized.
        - This helper implements subtraction at the parts level; callers handle higher-level sign semantics
          when necessary. Borrow/propagation is handled by subtract_magnitude.
    """
    # Now both are positive numbers
    comparison: int = compare_magnitude(a_parts, b_parts)

    if comparison >= 0:
        result_normalized_parts = subtract_magnitude(a_parts, b_parts)

    else:
        result_normalized_parts = subtract_magnitude(b_parts, a_parts)
        # Result will be negative
        result_normalized_parts = SexagesimalParts(
            is_negative=True,
            integer_part=result_normalized_parts.integer_part,
            fractional_part=result_normalized_parts.fractional_part,
        )

    return result_normalized_parts
