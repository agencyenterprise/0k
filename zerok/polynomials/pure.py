from zerok.commitments.mkzg.ecc import curve_order
from sympy.polys.domains import FiniteField as _FiniteField
from sympy.polys.domains.modularinteger import ModularInteger as _ModularInteger
from sympy.polys.domains import ZZ
from zerok.polynomials.types import ArithmetizationType
import random

PRIME_MODULO = curve_order  # 2**255 - 19
PRECISION_BITS = 64
SCALE = 2**PRECISION_BITS
NEGATIVE_POINT = PRIME_MODULO // 2
ROUND_PRECISION = 50
PRECISION_THRESHOLD = 3.999999999999999999999999999999999999999999999999


_dom = ZZ
_mod = PRIME_MODULO
_sym = True
parent = _FiniteField(_mod)


class ModularInteger(_ModularInteger):
    mod, dom, sym = _mod, _dom, _sym
    _parent = parent
    arithmetization_type: ArithmetizationType = ArithmetizationType.PURE

    def __init__(self, val, scale=True):
        super().__init__(val)
        if _sym:
            self.__name__ = "SymmetricModularIntegerMod%s" % _mod
        else:
            self.__name__ = "ModularIntegerMod%s" % _mod

    @staticmethod
    def random():
        return ModularInteger(random.randint(0, PRIME_MODULO - 1))

    @staticmethod
    def arithmetic_type() -> ArithmetizationType:
        return ArithmetizationType.PURE

    def inverse(self):
        return self**-1


class FiniteField(_FiniteField):
    zero = ModularInteger(0)
    one = ModularInteger(1)
    two = ModularInteger(2)
    arithmetization_type: ArithmetizationType = ArithmetizationType.PURE

    def __init__(self, mod):
        super().__init__(mod)

    def __call__(self, val, scale=True):
        return ModularInteger(val)

    @staticmethod
    def arithmetic_type() -> ArithmetizationType:
        return ArithmetizationType.PURE


ModularInteger._parent = FiniteField(PRIME_MODULO)


def qdiv(a: ModularInteger, b: ModularInteger) -> ModularInteger:
    return a * b**-1


def qexp(a: ModularInteger, b: int) -> ModularInteger:
    return a**b


def qmul(a: ModularInteger, b: ModularInteger) -> ModularInteger:
    return a * b


def qadd(a: ModularInteger, b: ModularInteger) -> ModularInteger:
    return a + b


def float_to_mod_float(value: ModularInteger) -> int:
    return value.val if hasattr(value, "val") else value


def quantization(value: float) -> ModularInteger:
    return ModularInteger(value * SCALE)


def dequantization(value: ModularInteger) -> float:
    return int(value.val)


DOMAIN = parent
