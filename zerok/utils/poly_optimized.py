from enum import Enum

from numpy.polynomial import polynomial as P

from zerok.utils.curve_optimized import Scalar


class Basis(Enum):
    LAGRANGE = 1
    MONOMIAL = 2


class Polynomial:
    values: list[Scalar]
    # when basis is LAGRANGE, len(values) should be power of 2
    basis: Basis

    def __str__(self):
        return f"values: {self.values}, basis: {self.basis}"

    def __init__(self, values: list[Scalar], basis: Basis = Basis.MONOMIAL):
        assert all(isinstance(x, Scalar) for x in values)
        assert isinstance(basis, Basis)
        self.values = values
        self.basis = basis

    def __eq__(self, other):
        return (self.basis == other.basis) and (self.values == other.values)

    def __add__(self, other):
        if isinstance(other, Polynomial):
            assert self.basis == other.basis
            if self.basis == Basis.LAGRANGE:
                assert len(self.values) == len(other.values)
                return Polynomial(
                    [x + y for x, y in zip(self.values, other.values)],
                    self.basis,
                )

            if self.basis == Basis.MONOMIAL:
                res = P.polyadd(self.values, other.values)
                return Polynomial(
                    res,
                    self.basis,
                )
        else:
            assert isinstance(other, Scalar)
            if self.basis == Basis.LAGRANGE:
                return Polynomial(
                    [x + other for x in self.values],
                    self.basis,
                )

            if self.basis == Basis.MONOMIAL:
                res = P.polyadd(self.values, [other])
                return Polynomial(
                    res,
                    self.basis,
                )

    def __sub__(self, other):
        if isinstance(other, Polynomial):
            assert self.basis == other.basis
            if self.basis == Basis.LAGRANGE:
                assert len(self.values) == len(other.values)
                return Polynomial(
                    [x - y for x, y in zip(self.values, other.values)],
                    self.basis,
                )

            if self.basis == Basis.MONOMIAL:
                res = P.polysub(self.values, other.values)
                return Polynomial(
                    res,
                    self.basis,
                )
        else:
            assert isinstance(other, Scalar)
            if self.basis == Basis.LAGRANGE:
                return Polynomial(
                    [x - other for x in self.values],
                    self.basis,
                )

            if self.basis == Basis.MONOMIAL:
                res = P.polysub(self.values, [other])
                return Polynomial(
                    res,
                    self.basis,
                )

    def __neg__(self):
        return Polynomial([Scalar(0)]) - self

    def __mul__(self, other):
        if isinstance(other, Polynomial):
            assert self.basis == other.basis
            if self.basis == Basis.LAGRANGE:
                assert len(self.values) == len(other.values)
                res = [x * y for x, y in zip(self.values, other.values)]
            if self.basis == Basis.MONOMIAL:
                c1 = self.values
                c2 = other.values
                res = P.polymul(c1, c2)

            return Polynomial(
                res,
                self.basis,
            )
        else:
            assert isinstance(other, Scalar)
            if self.basis == Basis.LAGRANGE:
                return Polynomial(
                    [x * other for x in self.values],
                    self.basis,
                )

            if self.basis == Basis.MONOMIAL:
                c1 = self.values
                c2 = [other]
                res = P.polymul(c1, c2)
                return Polynomial(
                    res,
                    self.basis,
                )

    def __truediv__(self, other):
        if isinstance(other, Polynomial):
            assert self.basis == other.basis
            if self.basis == Basis.LAGRANGE:
                assert len(self.values) == len(other.values)
                return Polynomial(
                    [x / y for x, y in zip(self.values, other.values)],
                    self.basis,
                )
            if self.basis == Basis.MONOMIAL:
                qx, rx = P.polydiv(self.values, other.values)
                # here we only consider the scenario of remainder is 0
                assert list(rx) == [0]

                return Polynomial(
                    qx,
                    self.basis,
                )
        else:
            assert isinstance(other, Scalar)
            return Polynomial(
                [x / other for x in self.values],
                self.basis,
            )

    def compose(self, other):
        assert self.basis == Basis.MONOMIAL
        assert other.basis == Basis.MONOMIAL

        result = Polynomial([self.values[0]])
        current = other
        for i in range(1, len(self.values)):
            result += Polynomial([self.values[i]]) * current
            current *= other
        return result

    def shift(self, shift: int):
        assert self.basis == Basis.LAGRANGE
        assert shift < len(self.values)

        return Polynomial(
            self.values[shift:] + self.values[:shift],
            self.basis,
        )

    # Convenience method to do FFTs specifically over the subgroup over which
    # all of the proofs are operating
    def fft(self, inv=False):
        order = len(self.values)
        assert order == 2 ** (order.bit_length() - 1)

        # Fast Fourier transform, used to convert between polynomial coefficients
        # and a list of evaluations at the roots of unity
        # See https://vitalik.ca/general/2019/05/12/fft.html
        def _fft(vals, modulus, roots_of_unity):
            if len(vals) == 1:
                return vals
            L = _fft(vals[::2], modulus, roots_of_unity[::2])
            R = _fft(vals[1::2], modulus, roots_of_unity[::2])
            o = [0] * len(vals)
            for i, (x, y) in enumerate(zip(L, R)):
                y_times_root = y * roots_of_unity[i]
                o[i] = (x + y_times_root) % modulus
                o[i + len(L)] = (x - y_times_root) % modulus
            return o

        roots = [x.n for x in Scalar.roots_of_unity(len(self.values))]
        o, nvals = Scalar.field_modulus, [x.n for x in self.values]
        if inv:
            assert self.basis == Basis.LAGRANGE
            # Inverse FFT
            invlen = Scalar(1) / len(self.values)
            reversed_roots = [roots[0]] + roots[1:][::-1]
            return Polynomial(
                [Scalar(x) * invlen for x in _fft(nvals, o, reversed_roots)],
                Basis.MONOMIAL,
            )
        else:
            assert self.basis == Basis.MONOMIAL
            # Regular FFT
            return Polynomial(
                [Scalar(x) for x in _fft(nvals, o, roots)], Basis.LAGRANGE
            )

    def ifft(self):
        return self.fft(True)

    # Given a polynomial expressed as a list of evaluations at roots of unity,
    # evaluate it at x directly, without using an FFT to covert to coeffs first
    # https://hackmd.io/@vbuterin/barycentric_evaluation
    def barycentric_eval(self, x: Scalar):
        assert self.basis == Basis.LAGRANGE

        order = len(self.values)
        assert order == 2 ** (order.bit_length() - 1)

        roots_of_unity = Scalar.roots_of_unity(order)
        elem = x.n % Scalar.field_modulus
        if elem in roots_of_unity:
            return self.values[roots_of_unity.index(elem)]

        first = (x**order - 1) / order
        second = sum(
            [
                value * root / (x - root)
                for value, root in zip(self.values, roots_of_unity)
            ]
        )
        return first * second

    # Evaluate at x directly for polynomial of MONOMIAL
    # This is inefficient, just for study usage
    def coeff_eval(self, x: Scalar):
        assert self.basis == Basis.MONOMIAL
        coeffs = self.values
        result = coeffs[0]
        for i in range(1, len(coeffs)):
            result = result + coeffs[i] * x**i
        return result

    def eval(self, x: Scalar):
        if self.basis == Basis.LAGRANGE:
            y = self.barycentric_eval(x)
            return y
        else:
            return self.coeff_eval(x)

    # E.g. f(X) -> f(aX)
    def scale(self, a: Scalar):
        assert self.basis == Basis.MONOMIAL
        # Multiply each coefficient by a to the power of its degree
        new_values = [coeff * (a**i) for i, coeff in enumerate(self.values)]

        return Polynomial(new_values)
