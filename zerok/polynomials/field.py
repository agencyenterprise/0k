from typing import Union
import math
import random
from zerok.commitments.mkzg.ecc import curve_order

PRIME_MODULO = curve_order  # 2**255 - 19
PRECISION_BITS = 64
SCALE = 2**PRECISION_BITS
NEGATIVE_POINT = PRIME_MODULO // 2
ROUND_PRECISION = 50
PRECISION_THRESHOLD = 3.999999999999999999999999999999999999999999999999


def truncate(f, n):
    return math.floor(f * 10**n) / 10**n


def quantization(x, precision_bits=PRECISION_BITS, modulus=PRIME_MODULO):
    """
    Quantize a real number x with handling for negative values.

    Args:
    x (float): The real number to quantize.
    precision_bits (int): The number of bits of precision.
    modulus (int): The modulus of the finite field.

    Returns:
    int: The quantized value.
    """

    sign = 1 if x >= 0 else -1
    x = abs(x)
    quantization_scale = 2**precision_bits
    x_quantized = int(round(x * quantization_scale, 0))

    if sign < 0:
        x_quantized = (modulus - x_quantized) % modulus

    return x_quantized


def dequantization(
    x_quantized,
    precision_bits=PRECISION_BITS,
    modulus=PRIME_MODULO,
    negative_point=NEGATIVE_POINT,
):
    """
    Dequantize a value from a finite field back to a floating-point number, considering negative values.

    Args:
    x_quantized (FiniteField element): The quantized value in the finite field.
    precision_bits (int): The number of bits of precision.
    modulus (int): The modulus of the finite field.
    negative_point (int): The point above which values are considered negative.

    Returns:
    float: The dequantized floating-point number.
    """
    quantization_scale = 2**precision_bits
    x_int = int(x_quantized)  # Convert to integer for calculations

    # Handle negative values represented in two's complement
    if x_int > negative_point:
        x_int = x_int - modulus

    x_dequantized = x_int / quantization_scale
    return round(x_dequantized, ROUND_PRECISION)


def qmul(a, b, modulus=PRIME_MODULO, precision_bits=PRECISION_BITS):
    """
    Multiply two quantized numbers within a finite field and adjust by dividing
    by the quantization scale to handle the increased scale from multiplication.

    Args:
    a (FiniteField element): The first quantized value.
    b (FiniteField element): The second quantized value.
    modulus (int): The modulus of the finite field.
    precision_bits (int): The number of bits of precision.

    Returns:
    FiniteField: The result of the multiplication, correctly scaled.
    """
    if hasattr(a, "val"):
        a = a.val
    elif not isinstance(a, int) and not isinstance(a, float):
        raise ValueError("a must be an integer or float")
    if hasattr(b, "val"):
        b = b.val
    elif not isinstance(b, int) and not isinstance(b, float):
        raise ValueError("b must be an integer or float")
    a = dequantization(a)
    b = dequantization(b)
    return quantization(a * b)


def qadd(a, b, modulus=PRIME_MODULO, precision_bits=PRECISION_BITS):
    """
    Add two quantized numbers within a finite field.

    Args:
    a (FiniteField element): The first quantized number.
    b (FiniteField element): The second quantized number.
    modulus (int): The modulus of the finite field.

    Returns:
    FiniteField: The result of the addition.
    """
    # Addition within the finite field
    if hasattr(a, "val"):
        a = a.val
    if hasattr(b, "val"):
        b = b.val
    return int(a + b) % modulus


def qexp(base, exponent, modulus=PRIME_MODULO, precision_bits=PRECISION_BITS):
    """
    Exponentiate a base to a power using defined finite field multiplication (qmul).

    Args:
    base (int or FiniteField element): The base of the exponentiation.
    exponent (int): The exponent to which the base is raised.
    modulus (int): The modulus of the finite field.
    precision_bits (int): The number of precision bits used in qmul for scaling.

    Returns:
    FiniteField element: The result of the exponentiation.
    """
    if hasattr(base, "val"):
        return quantization(dequantization(base.val) ** exponent)
    return quantization(dequantization(base) ** exponent)


def qdiv(a, b):
    """
    Perform fixed-point division on scaled integers, correctly handling negative numbers.

    Args:
    a (int): The quantized numerator, already scaled by 2^precision_bits.
    b (int): The quantized denominator, already scaled by 2^precision_bits.
    precision_bits (int): The number of fractional bits in the fixed-point representation.

    Returns:
    int: The result of the division, scaled by 2^precision_bits.
    """
    if hasattr(a, "val"):
        a = a.val
    elif not isinstance(a, int) and not isinstance(a, float):
        raise ValueError("a must be an integer or float")
    if hasattr(b, "val"):
        b = b.val
    elif not isinstance(b, int) and not isinstance(b, float):
        raise ValueError("b must be an integer or float")
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    b = dequantization(b)
    a = dequantization(a)
    result = a / b
    return quantization(result)


def qcompare(a, b, modulus=PRIME_MODULO):
    """Helper function to adjust numbers based on their value relative to modulus/2."""
    if a >= NEGATIVE_POINT:
        a -= modulus
    if b >= NEGATIVE_POINT:
        b -= modulus
    return a, b


def qlt(a, b):
    """Less than comparison for quantized numbers."""
    a, b = dequantization(a), dequantization(b)
    return a < b


def qgt(a, b):
    """Greater than comparison for quantized numbers."""
    a, b = dequantization(a), dequantization(b)
    return a > b


def qle(a, b):
    """Less than or equal comparison for quantized numbers."""
    a, b = dequantization(a), dequantization(b)
    return a <= b


def qge(a, b):
    """Greater than or equal comparison for quantized numbers."""
    a, b = dequantization(a), dequantization(b)
    return a >= b


def qne(a, b):
    """Not equal comparison for quantized numbers."""
    # @TODO: This is a temporary fix to avoid floating point errors. We need to find a better way to compare
    # precision = 0
    # return round(dequantization(a.val), precision) != round(
    #     dequantization(b.val), precision
    # )
    # return truncate(dequantization(a.val), precision) != truncate(
    #     dequantization(b.val), precision
    # ) and round(dequantization(a.val), precision) != round(
    #     dequantization(b.val), precision
    # )
    a = dequantization(dequantization(a.val))
    b = dequantization(dequantization(b.val))
    # threhsold = 0.01
    # if a > 1e8 or b > 1e8:
    #     threhsold = 1e-8
    return abs(a - b) > 1e-8


def eq(a, b):
    """Equal comparison for quantized numbers."""
    # precision = 0
    # return truncate(dequantization(a.val), precision) == truncate(
    #     dequantization(b.val), precision
    # ) and round(dequantization(a.val), precision) != round(
    #     dequantization(b.val), precision
    # )
    # return round(dequantization(a.val), precision) != round(
    #     dequantization(b.val), precision
    # )
    a = dequantization(dequantization(a.val))
    b = dequantization(dequantization(b.val))
    return abs(a - b) <= 1e-8


def float_to_mod_float(value: Union[float, "ModularInteger"]) -> float:
    """Convert a floating-point number to a modular floating-point number.

    Args:
        value (Union[float, &quot;ModularInteger&quot;]): value to convert

    Returns:
        float: converted value
    """
    MAX_FLOAT = 3.999999999999
    MAX_INT = quantization(MAX_FLOAT)

    # Step 1: Convert the float to an integer by multiplying by 2^64
    if hasattr(value, "val"):
        converted_value = value.val
    else:
        converted_value = value

    mod_value = converted_value % MAX_INT
    result = dequantization(mod_value)

    result = round(result, ROUND_PRECISION)
    return quantization(result)


def generate_random_modular_float() -> float:
    """Generate a random modular floating-point number.

    Returns:
        float: random modular floating-point number
    """

    random_value = random.uniform(0, PRECISION_THRESHOLD)

    rounded_value = round(random_value, ROUND_PRECISION)

    # Step 3: Apply the quantization (assuming you want the result in quantized form)
    return quantization(rounded_value)


class ModularInteger:
    def __init__(self, val: float, scale=True):
        if scale:
            self.val = quantization(val)
        else:
            self.val = val

    def __int__(self):
        return int(self.val)

    def __lt__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qlt(self.val, other.val)

    def __gt__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qgt(self.val, other.val)

    def __le__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qle(self.val, other.val)

    def __ge__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qge(self.val, other.val)

    def __ne__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return qne(self, other)

    def __eq__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return eq(self, other)

    def __neg__(self):
        return ModularInteger(quantization(-dequantization(self.val)), False)

    def __add__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return ModularInteger(qadd(self, other), False)

    def __sub__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return ModularInteger(qadd(self, -other), False)

    def __mul__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return ModularInteger(qmul(self, other), False)

    def __truediv__(self, other: "ModularInteger"):
        if isinstance(other, ModularInteger):
            other = ModularInteger(other.val, False)
        if isinstance(other, float):
            other = ModularInteger(other, True)
        if isinstance(other, int):
            other = ModularInteger(other, True)
        return ModularInteger(qdiv(self, other), False)

    def __pow__(self, exponent: Union[int, float]):
        if not isinstance(exponent, int):
            raise ValueError("Exponent must be an integer")
        return ModularInteger(qexp(self, exponent % PRIME_MODULO), False)

    def inverse(self):
        one = ModularInteger(1)
        return one / self

    @staticmethod
    def random():
        return ModularInteger(generate_random_modular_float(), False)

    def float_to_mod_float(
        self, value: Union[float, "ModularInteger"]
    ) -> "ModularInteger":
        return ModularInteger(float_to_mod_float(value), False)

    def __repr__(self) -> str:
        return f"({self.val}, {dequantization(self.val)})"

    def __str__(self) -> str:
        return f"({self.val}, {dequantization(self.val)})"


class FiniteField:
    zero = ModularInteger(0, True)
    one = ModularInteger(1, True)

    def characteristic(self):
        return self.mod

    def __init__(self, mod: int):
        self.mod = mod

    def __call__(self, val: float, scale=False):
        return ModularInteger(val, scale)


DOMAIN = FiniteField(PRIME_MODULO)
