import pytest
from zerok.polynomials.utils.base import FP16x16Base

DEFAULT_PRECISION = 7  # Equivalent to 1e-4


def _get_FP16x16(value):
    if not isinstance(value, FP16x16Base):
        sign = value < 0
        if sign:
            value = -value
        if isinstance(value, int):
            return FP16x16Base(value, sign)
        raise ValueError(
            "Expected value must be an instance of FP16x16 when using assert_relative"
        )
    return value


def assert_precise(result, expected, msg, custom_precision=None):
    result = _get_FP16x16(result)
    expected = _get_FP16x16(expected)

    precision = custom_precision if custom_precision is not None else DEFAULT_PRECISION
    diff = abs(result - expected)
    if diff._mag > precision:
        pytest.fail(
            f"{msg}: Expected {expected} with precision {precision}, but got {result}"
        )


def assert_relative(result, expected, msg, custom_precision=None):
    result = _get_FP16x16(result)
    expected = _get_FP16x16(expected)

    precision = custom_precision if custom_precision is not None else DEFAULT_PRECISION
    diff = abs(result - expected)

    # Avoid division by zero by checking if the result is zero
    if result == 0:
        rel_diff = diff
    else:
        rel_diff = diff / abs(result)

    if rel_diff._mag > precision:
        pytest.fail(
            f"{msg}: Expected {expected} with precision {precision}, but got {result}, difference: {diff._mag}, relative difference: {rel_diff._mag}"
        )
