from typing import Union
import math
import random
from zerok.commitments.mkzg.ecc import curve_order
from zerok.polynomials.types import ArithmetizationType

PRIME_MODULO = curve_order  # 2**255 - 19
PRECISION_BITS = 64
SCALE = 2**PRECISION_BITS
NEGATIVE_POINT = PRIME_MODULO // 2
ROUND_PRECISION = 50
PRECISION_THRESHOLD = 3.999999999999999999999999999999999999999999999999
FINITE_FIELD = True


class ModularArithmeticManager:
    def __init__(
        self, arithmetization_type: ArithmetizationType = ArithmetizationType.PURE
    ):
        self.arithmetization_type = arithmetization_type
        self._set_imports()

    def _set_imports(self):
        if self.arithmetization_type == ArithmetizationType.FLOAT_SYMMETRIC:
            from zerok.polynomials.symmetric_quantization_field import (
                ModularInteger,
                FiniteField,
                qdiv,
                dequantization,
                qmul,
                qadd,
                qexp,
                qcompare,
                qge,
                qgt,
                qle,
                qlt,
                qne,
                quantization,
                eq,
                float_to_mod_float,
                generate_random_modular_float,
                DOMAIN,
            )

            _ModularInterger = ModularInteger
        elif self.arithmetization_type == ArithmetizationType.PURE:
            from zerok.polynomials.pure import (
                ModularInteger,
                _ModularInteger as BaseModularInteger,
                FiniteField,
                qdiv,
                dequantization,
                qmul,
                qadd,
                qexp,
                quantization,
                float_to_mod_float,
                DOMAIN,
            )

            base_comparator = lambda name: lambda a, b: NotImplementedError(
                f"{name} Not implemented"
            )
            qge = base_comparator("qge")
            qgt = base_comparator("qgt")
            qle = base_comparator("qle")
            qlt = base_comparator("qlt")
            qne = base_comparator("qne")
            eq = base_comparator("eq")
            qcompare = base_comparator("qcompare")
            generate_random_modular_float = lambda: NotImplementedError(
                "generate_random_modular_float Not implemented"
            )
            _ModularInterger = BaseModularInteger
        elif self.arithmetization_type == ArithmetizationType.FLOAT_ASYMMETRIC:
            from zerok.polynomials.asymmetric_quantization_field import (
                ModularInteger,
                FiniteField,
                FP16x16Base,
                qdiv,
                dequantization,
                qmul,
                qadd,
                qexp,
                qcompare,
                qge,
                qgt,
                qle,
                qlt,
                qne,
                quantization,
                eq,
                float_to_mod_float,
                generate_random_modular_float,
                DOMAIN,
            )

            _ModularInterger = FP16x16Base
        else:
            raise ValueError("Invalid arithmetization type")

        self.ModularInteger = ModularInteger
        self._ModularInteger = _ModularInterger
        self.FiniteField = FiniteField
        self.qdiv = qdiv
        self.dequantization = dequantization
        self.qmul = qmul
        self.qadd = qadd
        self.qexp = qexp
        self.quantization = quantization
        self.float_to_mod_float = float_to_mod_float
        self.DOMAIN = DOMAIN
        self.qge = qge
        self.qgt = qgt
        self.qle = qle
        self.qlt = qlt
        self.qne = qne
        self.eq = eq
        self.qcompare = qcompare
        self.generate_random_modular_float = generate_random_modular_float
        self.curve_order = curve_order
        self.SCALE = SCALE
        self.ROUND_PRECISION = ROUND_PRECISION
        self.PRECISION_THRESHOLD = PRECISION_THRESHOLD
        self.PRECISION_BITS = PRECISION_BITS
        self.NEGATIVE_POINT = NEGATIVE_POINT
        self.ArithmetizationType = ArithmetizationType
        # Update globals dynamically
        globals().update(
            {
                "ModularInteger": ModularInteger,
                "_ModularInteger": _ModularInterger,
                "FiniteField": FiniteField,
                "qdiv": qdiv,
                "dequantization": dequantization,
                "qmul": qmul,
                "qadd": qadd,
                "qexp": qexp,
                "quantization": quantization,
                "float_to_mod_float": float_to_mod_float,
                "DOMAIN": DOMAIN,
                "qge": qge,
                "qgt": qgt,
                "qle": qle,
                "qlt": qlt,
                "qne": qne,
                "eq": eq,
                "qcompare": qcompare,
                "generate_random_modular_float": generate_random_modular_float,
                "curve_order": curve_order,
                "SCALE": SCALE,
                "ROUND_PRECISION": ROUND_PRECISION,
                "PRECISION_THRESHOLD": PRECISION_THRESHOLD,
                "PRECISION_BITS": PRECISION_BITS,
                "NEGATIVE_POINT": NEGATIVE_POINT,
                "ArithmetizationType": ArithmetizationType,
            }
        )

    def switch_imports(self, arithmetization_type: ArithmetizationType):
        """Switches the imports globally to the chosen mode."""
        self.arithmetization_type = arithmetization_type
        self._set_imports()


field_manager = ModularArithmeticManager(ArithmetizationType.FLOAT_SYMMETRIC)


def switch_global_imports(arithmetization_type: ArithmetizationType):
    """Function to switch the global imports on the fly."""
    field_manager.switch_imports(arithmetization_type)
