from zerok.utils.curve import G1Point, Scalar
from zerok.utils.poly import Polynomial, Basis
from zerok.commitments.kzg.kzg import Setup


def test_kzg_commitment():
    setup = Setup.from_file("./tests/assets/powersOfTau28_hez_final_11.ptau")
    dummy_values = Polynomial(
        list(map(Scalar, [1, 2, 3, 4, 5, 6, 7, 8])), Basis.LAGRANGE
    )
    commitment = setup.commit_G1(dummy_values)
    assert commitment == G1Point(
        (
            16120260411117808045030798560855586501988622612038310041007562782458075125622,
            3125847109934958347271782137825877642397632921923926105820408033549219695465,
        )
    )
