from zerok.polynomials.utils.lookup import atan_lut, sin_lut, exp2_lut, msb_lut
from uuid import uuid4

# Constants
HALF = 2**15
ONE = 2**16
TWO = 2**17
MAX = 2**31

TWO_PI = 411775
PI = 205887
HALF_PI = 102944


class FP16x16Base:
    def __init__(self, mag: int, sign: bool = False):
        self._mag = mag
        self.val = self._mag
        self._sign = sign
        self.id: int = uuid4().int

    @property
    def _mag(self) -> int:
        return self.__mag

    @_mag.setter
    def _mag(self, value: int):
        if value < 0:
            raise ValueError("Magnitude must be non-negative")
        self.__mag = value

    @staticmethod
    def ZERO() -> "FP16x16Base":
        return FP16x16Base(0)

    @staticmethod
    def HALF() -> "FP16x16Base":
        return FP16x16Base(HALF)

    @staticmethod
    def ONE() -> "FP16x16Base":
        return FP16x16Base(ONE)

    @staticmethod
    def MAX() -> "FP16x16Base":
        return FP16x16Base(MAX)

    @staticmethod
    def new(mag: int, sign: bool = False) -> "FP16x16Base":
        return FP16x16Base(mag, sign)

    @staticmethod
    def dequantization(value: "FP16x16Base") -> float:
        mag = value._mag
        sign = value._sign
        return mag / ONE if not sign else -mag / ONE

    @staticmethod
    def quantization(value: float) -> "FP16x16Base":
        sign = value < 0
        return FP16x16Base(int(abs(value) * ONE), sign)

    @staticmethod
    def new_unscaled(mag: int, sign: bool = False) -> "FP16x16Base":
        assert (isinstance(mag, int)) and (0 <= mag < MAX), "Invalid mag"
        return FP16x16Base(mag * ONE, sign)

    def __abs__(self) -> "FP16x16Base":
        return FP16x16Base.new(self._mag, False)

    def ceil(self) -> "FP16x16Base":
        div, rem = divmod(self._mag, ONE)

        if rem == 0:
            return FP16x16Base(self._mag, self._sign)
        elif not self._sign:
            return FP16x16Base.new_unscaled(div + 1, False)
        elif div == 0:
            return FP16x16Base.new_unscaled(0, False)
        else:
            return FP16x16Base.new_unscaled(div, True)

    def floor(self) -> "FP16x16Base":
        div, rem = divmod(self._mag, ONE)

        if rem == 0:
            return FP16x16Base(self._mag, self._sign)
        elif not self._sign:
            return FP16x16Base.new_unscaled(div, False)
        else:
            return FP16x16Base.new_unscaled(div + 1, True)

    def exp(self) -> "FP16x16Base":
        log2_e = FP16x16Base(94548)  # log2(e) * 2^23 ≈ 12102203
        b = log2_e * self
        return b.exp2()

    def exp2(self) -> "FP16x16Base":
        if self._mag == 0:
            return FP16x16Base.ONE()

        int_part, frac_part = divmod(self._mag, ONE)
        int_res = FP16x16Base.new_unscaled(exp2_lut(int_part), False)
        res_u = int_res

        if frac_part != 0:
            frac = FP16x16Base(frac_part)
            r7 = FP16x16Base(1) * frac
            r6 = (r7 + FP16x16Base(10)) * frac
            r5 = (r6 + FP16x16Base(87)) * frac
            r4 = (r5 + FP16x16Base(630)) * frac
            r3 = (r4 + FP16x16Base(3638)) * frac
            r2 = (r3 + FP16x16Base(15743)) * frac
            r1 = (r2 + FP16x16Base(45426)) * frac
            res_u = res_u * (r1 + FP16x16Base.ONE())

        if self._sign:
            return FP16x16Base.ONE() / res_u
        else:
            return res_u

    @staticmethod
    def exp2_int(exp: int) -> "FP16x16Base":
        # Use the lookup table to get the result of 2^exp
        return FP16x16Base.new_unscaled(exp2_lut(exp), False)

    def log2(self) -> "FP16x16Base":
        assert not self._sign, "must be positive"

        if self._mag == ONE:
            return FP16x16Base.ZERO()

        if self._mag < ONE:
            a_div = FP16x16Base.ONE() / self
            return -(a_div.log2())

        whole = self._mag // ONE
        msb, div = msb_lut(whole)

        if self._mag == div * ONE:
            return FP16x16Base.new_unscaled(msb, False)
        else:
            norm = self / FP16x16Base.new_unscaled(div, False)
            r8 = FP16x16Base(596, True) * norm
            r7 = (r8 + FP16x16Base(8116, False)) * norm
            r6 = (r7 + FP16x16Base(49044, True)) * norm
            r5 = (r6 + FP16x16Base(172935, False)) * norm
            r4 = (r5 + FP16x16Base(394096, True)) * norm
            r3 = (r4 + FP16x16Base(608566, False)) * norm
            r2 = (r3 + FP16x16Base(655828, True)) * norm
            r1 = (r2 + FP16x16Base(534433, False)) * norm

            return r1 + FP16x16Base(224487, True) + FP16x16Base.new_unscaled(msb, False)

    def ln(self) -> "FP16x16Base":
        ln2 = FP16x16Base(45426, False)  # ln(2) = 0.693...
        return self.log2() * ln2

    def log10(self) -> "FP16x16Base":
        log10_2 = FP16x16Base(19728, False)  # log10(2) = 0.301... in fixed-point
        return self.log2() * log10_2

    def __pow__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            other_sign = other < 0
            other = FP16x16Base.new_unscaled(abs(other), other_sign)
        _, rem = divmod(other._mag, ONE)

        # Use the more performant integer pow when b is an integer
        if rem == 0:
            return self.pow_int(other._mag // ONE, other._sign)

        # x^y = exp(y*ln(x)) for x > 0 will error for x < 0
        return (other * self.ln()).exp()

    def pow_int(self, b: int, sign: bool) -> "FP16x16Base":
        x = self
        n = b

        if sign:
            x = FP16x16Base.ONE().__truediv__(x)

        if n == 0:
            return FP16x16Base.ONE()

        y = FP16x16Base.ONE()

        while n > 1:
            div, rem = divmod(n, 2)

            if rem == 1:
                y = x * y

            x = x * x
            n = div

        return x * y

    def round(self) -> "FP16x16Base":
        div, rem = divmod(self._mag, ONE)

        if HALF <= rem:
            return FP16x16Base.new_unscaled(div + 1, self._sign)
        else:
            return FP16x16Base.new_unscaled(div, self._sign)

    def sqrt(self) -> "FP16x16Base":
        assert not self._sign, "must be positive"

        # Calculate the square root of the magnitude, scaled by ONE to maintain precision
        root = int((self._mag * ONE) ** 0.5)

        return FP16x16Base(root, False)

    def sign(self) -> "FP16x16Base":
        if self._mag == 0:
            return FP16x16Base(0, False)
        else:
            return FP16x16Base(ONE, self._sign)

    @staticmethod
    def NaN() -> "FP16x16Base":
        return FP16x16Base(0, True)

    def is_nan(self) -> bool:
        return self._mag == 0 and self._sign

    @staticmethod
    def INF() -> "FP16x16Base":
        return FP16x16Base(4294967295, False)

    @staticmethod
    def POS_INF() -> "FP16x16Base":
        return FP16x16Base.INF()

    @staticmethod
    def NEG_INF() -> "FP16x16Base":
        return FP16x16Base(4294967295, True)

    def is_inf(self) -> bool:
        return self._mag == 4294967295

    def is_pos_inf(self) -> bool:
        return self.is_inf() and not self._sign

    def is_neg_inf(self) -> bool:
        return self.is_inf() and self._sign

    def __eq__(self, other) -> bool:
        if isinstance(other, FP16x16Base):
            return self._mag == other._mag and self._sign == other._sign
        return NotImplemented

    def __ne__(self, other) -> bool:
        if isinstance(other, FP16x16Base):
            return self._mag != other._mag or self._sign != other._sign
        return NotImplemented

    def __add__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        if self._sign == other._sign:
            return FP16x16Base(self._mag + other._mag, self._sign)

        if self._mag == other._mag:
            return FP16x16Base.ZERO()

        if self._mag > other._mag:
            return FP16x16Base(self._mag - other._mag, self._sign)
        else:
            return FP16x16Base(other._mag - self._mag, other._sign)

    def __iadd__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        # Use the __add__ method to perform the addition and update self
        result = self.__add__(other)
        self._mag, self._sign = result._mag, result._sign
        return self

    def __neg__(self) -> "FP16x16Base":
        if self._mag == 0:
            return self
        else:
            return FP16x16Base(self._mag, not self._sign)

    def __sub__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        return self.__add__(-other)

    def __isub__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        # Use the __sub__ method to perform the subtraction and update self
        result = self.__sub__(other)
        self._mag, self._sign = result._mag, result._sign
        return self

    def __mul__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        # Perform wide multiplication and then shift back to the correct scale
        prod = (self._mag * other._mag) // ONE

        # Re-apply sign using XOR
        sign = self._sign != other._sign
        return FP16x16Base(prod, sign)

    def __imul__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        # Use the __mul__ method to perform the multiplication and update self
        result = self.__mul__(other)
        self._mag, self._sign = result._mag, result._sign
        return self

    def __truediv__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        # Perform wide division by first scaling up the dividend
        dividend = self._mag * ONE
        divisor = other._mag
        quotient = dividend // divisor

        # Re-apply sign using XOR
        sign = self._sign != other._sign
        return FP16x16Base(quotient, sign)

    def __rtruediv__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        return other.__truediv__(self)

    def __itruediv__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        # Use the __truediv__ method to perform the division and update self
        result = self.__truediv__(other)
        self._mag, self._sign = result._mag, result._sign
        return self

    def __ge__(self, other) -> bool:
        if not isinstance(other, FP16x16Base):
            other_sign = other < 0
            other = FP16x16Base.new_unscaled(abs(other), other_sign)

        if self._sign != other._sign:
            return not self._sign
        else:
            return (self._mag == other._mag) or ((self._mag > other._mag) != self._sign)

    def __gt__(self, other) -> bool:
        if not isinstance(other, FP16x16Base):
            other_sign = other < 0
            other = FP16x16Base.new_unscaled(abs(other), other_sign)

        if self._sign != other._sign:
            return not self._sign
        else:
            return (self._mag != other._mag) and (
                (self._mag > other._mag) != self._sign
            )

    def __le__(self, other) -> bool:
        if not isinstance(other, FP16x16Base):
            other_sign = other < 0
            other = FP16x16Base.new_unscaled(abs(other), other_sign)

        if self._sign != other._sign:
            return self._sign
        else:
            return (self._mag == other._mag) or ((self._mag < other._mag) != self._sign)

    def __lt__(self, other) -> bool:
        if not isinstance(other, FP16x16Base):
            other_sign = other < 0
            other = FP16x16Base.new_unscaled(abs(other), other_sign)

        if self._sign != other._sign:
            return self._sign
        else:
            return (self._mag != other._mag) and (
                (self._mag < other._mag) != self._sign
            )

    def __mod__(self, other) -> "FP16x16Base":
        if not isinstance(other, FP16x16Base):
            return NotImplemented

        # Compute the division, take the floor, and multiply by 'b', then subtract from 'a'
        quotient = self.__truediv__(other)
        quotient_floor = quotient.floor()
        return self - (quotient_floor * other)

    def __hash__(self) -> int:
        return hash((self._mag, self._sign))

    def __str__(self) -> str:
        return f"FP16x16Base({self._mag}, {self._sign})"

    def __repr__(self) -> str:
        return self.__str__()

    # trig

    def atan(self) -> "FP16x16Base":
        at = self.__abs__()
        shift = False
        invert = False

        # Invert value when a > 1
        if at._mag > ONE:
            at = FP16x16Base.ONE() / at
            invert = True

        # Account for lack of precision in polynomial when a > 0.7
        if at._mag > 45875:
            sqrt3_3 = FP16x16Base(37837, False)  # sqrt(3) / 3
            at = (at - sqrt3_3) / (FP16x16Base.ONE() + at * sqrt3_3)
            shift = True

        r10 = FP16x16Base(120, True) * at
        r9 = (r10 + FP16x16Base(3066, True)) * at
        r8 = (r9 + FP16x16Base(12727, False)) * at
        r7 = (r8 + FP16x16Base(17170, True)) * at
        r6 = (r7 + FP16x16Base(2865, False)) * at
        r5 = (r6 + FP16x16Base(12456, False)) * at
        r4 = (r5 + FP16x16Base(90, False)) * at
        r3 = (r4 + FP16x16Base(21852, True)) * at
        r2 = r3 * at
        res = (r2 + FP16x16Base(65536, False)) * at

        # Adjust for sign change, inversion, and shift
        if shift:
            res += FP16x16Base(34315, False)  # pi / 6

        if invert:
            res -= FP16x16Base(HALF_PI, False)

        return FP16x16Base(res._mag, self._sign)

    def atan_fast(self) -> "FP16x16Base":
        at = self.__abs__()
        shift = False
        invert = False

        # Invert value when a > 1
        if at._mag > ONE:
            at = FP16x16Base.ONE() / at
            invert = True

        # Account for lack of precision in polynomial when a > 0.7
        if at._mag > 45875:
            sqrt3_3 = FP16x16Base(37837, False)  # sqrt(3) / 3
            at = (at - sqrt3_3) / (FP16x16Base.ONE() + at * sqrt3_3)
            shift = True
        start, low, high = atan_lut(at._mag)
        partial_step = FP16x16Base(at._mag - start, False) / FP16x16Base(459, False)
        res = partial_step * FP16x16Base(high - low, False) + FP16x16Base(low, False)

        # Adjust for sign change, inversion, and shift
        if shift:
            res += FP16x16Base(34315, False)  # pi / 6

        if invert:
            res -= FP16x16Base(HALF_PI, False)

        return FP16x16Base(res._mag, self._sign)

    def asin_fast(self) -> "FP16x16Base":
        if self._mag == ONE:
            return FP16x16Base(HALF_PI, self._sign)

        div = (FP16x16Base.ONE() - self * self).sqrt()  # Will fail if a > 1
        b = self / div
        return b.atan_fast()

    def asin(self) -> "FP16x16Base":
        if self._mag == ONE:
            return FP16x16Base(HALF_PI, self._sign)

        div = (FP16x16Base.ONE() - self * self).sqrt()  # Will fail if a > 1
        b = self / div
        return b.atan()

    def acos(self) -> "FP16x16Base":
        asin_arg = (FP16x16Base.ONE() - self * self).sqrt()  # Will fail if a > 1
        asin_res = asin_arg.asin()

        if self._sign:
            return FP16x16Base(PI, False) - asin_res
        else:
            return asin_res

    def acos_fast(self) -> "FP16x16Base":
        asin_arg = (FP16x16Base.ONE() - self * self).sqrt()  # Will fail if a > 1
        asin_res = asin_arg.asin_fast()

        if self._sign:
            return FP16x16Base(PI, False) - asin_res
        else:
            return asin_res

    def cos(self) -> "FP16x16Base":
        value = FP16x16Base(HALF_PI, False) - self
        return value.sin()

    def cos_fast(self) -> "FP16x16Base":
        value = FP16x16Base(HALF_PI, False) - self
        return value.sin_fast()

    def sin(self) -> "FP16x16Base":
        a1 = self._mag % TWO_PI
        whole_rem, partial_rem = divmod(a1, PI)
        a2 = FP16x16Base(partial_rem, False)
        partial_sign = whole_rem == 1

        loop_res = a2 * self._sin_loop(a2, 7, FP16x16Base.ONE())

        return FP16x16Base(
            loop_res._mag, self._sign != partial_sign and loop_res._mag != 0
        )

    def sin_fast(self) -> "FP16x16Base":
        a1 = self._mag % TWO_PI
        whole_rem, partial_rem = divmod(a1, PI)
        partial_sign = whole_rem == 1

        if partial_rem >= HALF_PI:
            partial_rem = PI - partial_rem

        start, low, high = sin_lut(partial_rem)
        partial_step = FP16x16Base(partial_rem - start, False) / FP16x16Base(402, False)
        res = partial_step * (
            FP16x16Base(high, False) - FP16x16Base(low, False)
        ) + FP16x16Base(low, False)

        return FP16x16Base(res._mag, self._sign != partial_sign and res._mag != 0)

    def tan(self) -> "FP16x16Base":
        sinx = self.sin()
        cosx = self.cos()
        assert cosx._mag != 0, "tan undefined"

        return sinx / cosx

    def tan_fast(self) -> "FP16x16Base":
        sinx = self.sin_fast()
        cosx = self.cos_fast()
        assert cosx._mag != 0, "tan undefined"

        return sinx / cosx

    def _sin_loop(self, a: "FP16x16Base", i: int, acc: "FP16x16Base") -> "FP16x16Base":
        div = (2 * i + 2) * (2 * i + 3)
        term = a * a * acc / FP16x16Base.new_unscaled(div, False)
        new_acc = FP16x16Base.ONE() - term

        if i == 0:
            return new_acc

        return self._sin_loop(a, i - 1, new_acc)

    # hyp
    def cosh(self) -> "FP16x16Base":
        ea = self.exp()
        return (ea + (FP16x16Base.ONE() / ea)) / FP16x16Base(TWO, False)

    def sinh(self) -> "FP16x16Base":
        ea = self.exp()
        return (ea - (FP16x16Base.ONE() / ea)) / FP16x16Base(TWO, False)

    def tanh(self):
        ea = self.exp()
        ea_i = FP16x16Base.ONE() / ea
        return (ea - ea_i) / (ea + ea_i)

    def acosh(self) -> "FP16x16Base":
        root = (self * self - FP16x16Base.ONE()).sqrt()
        return (self + root).ln()

    def asinh(self) -> "FP16x16Base":
        root = (self * self + FP16x16Base.ONE()).sqrt()
        return (self + root).ln()

    def atanh(self) -> "FP16x16Base":
        one = FP16x16Base.ONE()
        ln_arg = (one + self) / (one - self)
        return ln_arg.ln() / FP16x16Base(TWO, False)

    def __int__(self):
        return int(self._mag * (1 if not self._sign else -1))
