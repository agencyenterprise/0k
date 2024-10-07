from zerok.commitments.mkzg.ecc import curve_order
from zerok.polynomials.utils.base import FP16x16Base
import random

PRIME_MODULO = curve_order  # 2**255 - 19
PRECISION_BITS = 64
SCALE = 2**PRECISION_BITS
NEGATIVE_POINT = PRIME_MODULO // 2
ROUND_PRECISION = 50
PRECISION_THRESHOLD = 3.999999999999999999999999999999999999999999999999


class ModularInteger(FP16x16Base):
    def __init__(self, x, scale=True):
        sign = x < 0
        if scale:
            x = FP16x16Base.new_unscaled(abs(x), sign)._mag
        super().__init__(abs(x), sign)
        self.val = self._mag

    def inverse(self):
        minus_one = ModularInteger(-1)
        return self**minus_one

    @staticmethod
    def random():
        # @TODO: Implement a better random number generator
        return ModularInteger(random.randint(0, 2**16 - 1))


class FiniteField:
    zero = ModularInteger(0)
    one = ModularInteger(1)
    two = ModularInteger(2)

    def __init__(self, prime_modulo):
        self.prime_modulo = prime_modulo

    def __call__(self, x, scale=True):
        # try:
        sign = x < 0
        return (
            ModularInteger.new_unscaled(x, sign)
            if scale
            else ModularInteger.new(x, sign)
        )

    # except Exception as e:
    #     print(e)
    #     sign = x < 0

    def characteristic(self):
        return self.prime_modulo


def qdiv(a: ModularInteger, b: ModularInteger) -> ModularInteger:
    return a * b**-1


def qexp(a: ModularInteger, b: int) -> ModularInteger:
    return a**b


def qmul(a: ModularInteger, b: ModularInteger) -> ModularInteger:
    return a * b


def qadd(a: ModularInteger, b: ModularInteger) -> ModularInteger:
    return a + b


def float_to_mod_float(value: ModularInteger) -> int:
    return value._mag if hasattr(value, "_mag") else value


def quantization(value: float) -> ModularInteger:
    return ModularInteger.quantization(value)


def dequantization(value: ModularInteger) -> float:
    return ModularInteger.dequantization(value)


# add these methods based on the Fp16x16Base class
# qcompare,
#                 qge,
#                 qgt,
#                 qle,
#                 qlt,
#                 qne,
#                 eq,


def qcompare(a: ModularInteger, b: ModularInteger) -> int:
    return a, b


def qge(a: ModularInteger, b: ModularInteger) -> bool:
    return a >= b


def qgt(a: ModularInteger, b: ModularInteger) -> bool:
    return a > b


def qle(a: ModularInteger, b: ModularInteger) -> bool:
    return a <= b


def qlt(a: ModularInteger, b: ModularInteger) -> bool:
    return a < b


def qne(a: ModularInteger, b: ModularInteger) -> bool:
    return a != b


def eq(a: ModularInteger, b: ModularInteger) -> bool:
    return a == b


def generate_random_modular_float():
    return ModularInteger.random()


DOMAIN = FiniteField(PRIME_MODULO)
