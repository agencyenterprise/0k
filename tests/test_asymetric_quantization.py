import pytest
from zerok.polynomials.utils.base import FP16x16Base as FP16x16, ONE, HALF
from zerok.polynomials.utils.lookup import exp2_lut
from zerok.polynomials.utils.utils import assert_precise, assert_relative
from zerok.polynomials.field import (
    switch_global_imports,
    ArithmetizationType,
    field_manager,
)

switch_global_imports(ArithmetizationType.FLOAT_ASYMMETRIC)
from zerok.graph.engine import Value
import numpy as np

from zerok.prover.prover import ZkProver

DOMAIN = field_manager.DOMAIN
dequantization = field_manager.dequantization


def test_circuit_generation_value_numpy():
    A = np.array([[Value(1), Value(2)], [Value(2), Value(1)]])
    B = np.array([[Value(3), Value(4)]])
    C = A * B
    assert len(C) == 2
    circuit, _, _ = Value.compile_layered_circuit(C[0][0], True)

    assert ZkProver(circuit).prove()


def test_mag_cannot_be_negative():
    with pytest.raises(ValueError, match="Magnitude must be non-negative"):
        FP16x16(-1, False)

    a = FP16x16(0, False)
    with pytest.raises(ValueError, match="Magnitude must be non-negative"):
        a._mag = -1


def test_eq():
    a = FP16x16.new_unscaled(42, False)
    b = FP16x16.new_unscaled(42, False)
    assert a == b, "invalid result"


def test_ne():
    a = FP16x16.new_unscaled(42, False)
    b = FP16x16.new_unscaled(43, False)  # Different magnitude
    c = FP16x16.new_unscaled(42, True)  # Different sign
    assert a != b, "invalid result"
    assert a != c, "invalid result"


def test_add():
    a = FP16x16.new_unscaled(1, False)
    b = FP16x16.new_unscaled(2, False)
    expected_sum = FP16x16.new_unscaled(3, False)
    assert a + b == expected_sum, "invalid result"


def test_add_eq():
    a = FP16x16.new_unscaled(1, False)
    b = FP16x16.new_unscaled(2, False)
    a += b
    expected_sum = FP16x16.new_unscaled(3, False)
    assert a == expected_sum, "invalid result"


def test_sub():
    a = FP16x16.new_unscaled(5, False)
    b = FP16x16.new_unscaled(2, False)
    expected_diff = FP16x16.new_unscaled(3, False)
    assert a - b == expected_diff, "false result invalid"


def test_sub_eq():
    a = FP16x16.new_unscaled(5, False)
    b = FP16x16.new_unscaled(2, False)
    a -= b
    expected_diff = FP16x16.new_unscaled(3, False)
    assert a == expected_diff, "invalid result"


def test_mul_pos():
    a = FP16x16(190054, False)
    b = FP16x16(190054, False)
    expected_prod = FP16x16(551155, False)
    assert a * b == expected_prod, "invalid result"


def test_mul_neg():
    a = FP16x16.new_unscaled(5, False)
    b = FP16x16.new_unscaled(2, True)
    expected_prod = FP16x16.new_unscaled(10, True)
    assert a * b == expected_prod, "invalid result"


def test_mul_eq():
    a = FP16x16.new_unscaled(5, False)
    b = FP16x16.new_unscaled(2, True)
    a *= b
    expected_prod = FP16x16.new_unscaled(10, True)
    assert a == expected_prod, "invalid result"


def test_div():
    a = FP16x16.new_unscaled(10, False)
    b = FP16x16(190054, False)  # 2.9 in fixed-point representation
    expected_quotient = FP16x16(225986, False)  # 3.4482758620689653 in fixed-point
    print("a/b -> ", a / b, expected_quotient)
    assert a / b == expected_quotient, "invalid pos decimal"


def test_le():
    a = FP16x16.new_unscaled(1, False)
    b = FP16x16.new_unscaled(0, False)
    c = FP16x16.new_unscaled(1, True)

    assert a <= a, "a <= a"
    assert not (a <= b), "a <= b"
    assert not (a <= c), "a <= c"

    assert b <= a, "b <= a"
    assert b <= b, "b <= b"
    assert not (b <= c), "b <= c"

    assert c <= a, "c <= a"
    assert c <= b, "c <= b"
    assert c <= c, "c <= c"


def test_lt():
    a = FP16x16.new_unscaled(1, False)
    b = FP16x16.new_unscaled(0, False)
    c = FP16x16.new_unscaled(1, True)

    assert not (a < a), "a < a"
    assert not (a < b), "a < b"
    assert not (a < c), "a < c"

    assert b < a, "b < a"
    assert not (b < b), "b < b"
    assert not (b < c), "b < c"

    assert c < a, "c < a"
    assert c < b, "c < b"
    assert not (c < c), "c < c"


def test_ge():
    a = FP16x16.new_unscaled(1, False)
    b = FP16x16.new_unscaled(0, False)
    c = FP16x16.new_unscaled(1, True)

    assert a >= a, "a >= a"
    assert a >= b, "a >= b"
    assert a >= c, "a >= c"

    assert not (b >= a), "b >= a"
    assert b >= b, "b >= b"
    assert b >= c, "b >= c"

    assert not (c >= a), "c >= a"
    assert not (c >= b), "c >= b"
    assert c >= c, "c >= c"


def test_gt():
    a = FP16x16.new_unscaled(1, False)
    b = FP16x16.new_unscaled(0, False)
    c = FP16x16.new_unscaled(1, True)

    assert not (a > a), "a > a"
    assert a > b, "a > b"
    assert a > c, "a > c"

    assert not (b > a), "b > a"
    assert not (b > b), "b > b"
    assert b > c, "b > c"

    assert not (c > a), "c > a"
    assert not (c > b), "c > b"
    assert not (c > c), "c > c"


def test_ceil():
    a = FP16x16(190054)  # 2.9 in fixed-point representation
    assert a.ceil()._mag == 3 * ONE, "invalid pos decimal"


def test_floor():
    a = FP16x16(190054)  # 2.9 in fixed-point representation
    assert a.floor()._mag == 2 * ONE, "invalid pos decimal"


def test_exp():
    a = FP16x16.new_unscaled(2)
    assert_relative(
        a.exp()._mag, 484249, "invalid exp of 2"
    )  # 7.389056098793725 in fixed-point


def test_exp2():
    a = FP16x16.new_unscaled(5)
    assert a.exp2()._mag == 2097152, "invalid exp2 of 2"


def test_exp2_int():
    assert FP16x16.exp2_int(5)._mag == exp2_lut(5) * ONE, "invalid exp2 of 2"


def test_ln():
    a = FP16x16.new_unscaled(1)
    assert_precise(a.ln()._mag, 0, "invalid ln of 1")

    a = FP16x16(178145)  # 2.7... in fixed-point representation
    assert_relative(a.ln()._mag, ONE, "invalid ln of 2.7...")


def test_log10():
    a = FP16x16.new_unscaled(100)
    expected_log10_100 = FP16x16.new_unscaled(2)  # log10(100) = 2
    assert_relative(a.log10()._mag, expected_log10_100._mag, "invalid log10")


def test_pow():
    a = FP16x16.new_unscaled(3)
    b = FP16x16.new_unscaled(4)
    expected_pow_3_4 = FP16x16.new_unscaled(81)  # 3^4 = 81
    assert_precise((a**b)._mag, expected_pow_3_4._mag, "invalid pos base power")


def test_pow_frac():
    a = FP16x16.new_unscaled(3)
    b = FP16x16(32768)  # 0.5 in fixed-point representation
    expected_pow_3_0_5 = 113512  # sqrt(3) ≈ 1.7320508075688772 in fixed-point
    assert_relative((a**b)._mag, expected_pow_3_0_5, "invalid pos base power")


def test_round():
    a = FP16x16(190054)  # 2.9 in fixed-point representation
    expected_rounded_value = FP16x16.new_unscaled(3)  # Rounded value of 2.9 is 3
    assert a.round()._mag == expected_rounded_value._mag, "invalid pos decimal"


def test_sqrt_fail():
    a = FP16x16.new_unscaled(25, True)
    with pytest.raises(AssertionError, match="must be positive"):
        a.sqrt()


def test_sqrt():
    a = FP16x16.new_unscaled(0, False)
    assert a.sqrt()._mag == 0, "invalid zero root"

    a = FP16x16.new_unscaled(25, False)
    expected_sqrt_25 = FP16x16.new_unscaled(5)  # sqrt(25) = 5
    assert a.sqrt()._mag == expected_sqrt_25._mag, "invalid pos root"


def test_sign():
    a = FP16x16(0, False)
    assert a.sign()._mag == 0 and not a.sign()._sign, "invalid sign (0, false)"

    a = FP16x16(HALF, True)
    assert a.sign()._mag == ONE and a.sign()._sign, "invalid sign (HALF, true)"

    a = FP16x16(HALF, False)
    assert a.sign()._mag == ONE and not a.sign()._sign, "invalid sign (HALF, false)"

    a = FP16x16(ONE, True)
    assert a.sign()._mag == ONE and a.sign()._sign, "invalid sign (ONE, true)"

    a = FP16x16(ONE, False)
    assert a.sign()._mag == ONE and not a.sign()._sign, "invalid sign (ONE, false)"


def test_sign_fail():
    a = FP16x16(HALF, True)
    with pytest.raises(AssertionError):
        assert (
            a.sign()._mag != ONE and a.sign()._sign is False
        ), "invalid sign (HALF, true)"


def test_nan():
    nan = FP16x16.NaN()
    assert nan.is_nan(), "NaN check failed"

    not_nan = FP16x16(1, False)
    assert not not_nan.is_nan(), "Non-NaN value incorrectly identified as NaN"


def test_inf():
    pos_inf = FP16x16.POS_INF()
    assert (
        pos_inf.is_inf() and pos_inf.is_pos_inf() and not pos_inf.is_neg_inf()
    ), "Positive infinity check failed"

    neg_inf = FP16x16.NEG_INF()
    assert (
        neg_inf.is_inf() and not neg_inf.is_pos_inf() and neg_inf.is_neg_inf()
    ), "Negative infinity check failed"

    not_inf = FP16x16(1, False)
    assert not not_inf.is_inf(), "Non-infinity value incorrectly identified as infinity"


def test_rem():
    a = FP16x16.new_unscaled(10, False)
    b = FP16x16.new_unscaled(3, False)
    expected_rem = FP16x16.new_unscaled(1, False)  # 10 % 3 = 1
    assert a % b == expected_rem, "invalid remainder"
