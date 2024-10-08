from zerok.graph.engine import Value
import numpy as np
from zerok.utils.visualize import draw_dot
from zerok.polynomials.field import dequantization, FiniteField, PRIME_MODULO
from zerok.prover.prover import ZkProver

DOMAIN = FiniteField(PRIME_MODULO)


def test_circuit_generation_value_numpy():
    A = np.array([[Value(1), Value(2)], [Value(2), Value(1)]])
    B = np.array([[Value(3), Value(4)]])
    C = A * B
    assert len(C) == 2
    circuit, _, _ = Value.compile_layered_circuit(C[0][0], True)

    assert ZkProver(circuit).prove()


def test_circuit_generation_value_scalars():
    A = Value(1)
    B = Value(2)
    C = A + B
    for i in range(2):
        one = Value(i)
        C = C * one
    circuit, _, layers = Value.compile_layered_circuit(C, True)
    draw_dot(layers[0][0]).render("tests/assets/scalars", format="png", cleanup=True)

    assert ZkProver(circuit).prove()
    assert dequantization(C.data) == dequantization(layers[0][0].data)


def test_circuit_generation_value_scalars_non_layered_operations():
    A = Value(3.0)
    B = Value(2.1)
    C = A * B
    D = Value(1)
    E = C * D
    F = B * E
    draw_dot(F).render(
        "tests/assets/value_scalars_non_layered_operations", format="png", cleanup=True
    )
    circuit, _, layers = Value.compile_layered_circuit(F, True)
    draw_dot(layers[0][0]).render(
        "tests/assets/value_scalars_non_layered_operations", format="png", cleanup=True
    )

    assert ZkProver(circuit).prove()
    assert dequantization(F.data) == dequantization(layers[0][0].data)


def test_circuit_generation_value_scalars_non_layered_operations_right():
    A = Value(3.77)
    B = Value(0.47)
    C = A + B
    D = A + B
    E = Value(0.05)
    F = D * E
    G = Value(0.99)
    H = F * G
    I = C * H
    draw_dot(I).render(
        "tests/assets/value_scalars_non_layered_operations_right",
        format="png",
        cleanup=True,
    )
    circuit, _, layers = Value.compile_layered_circuit(I, True)
    draw_dot(layers[0][0]).render(
        "tests/assets/value_scalars_non_layered_operations_right",
        format="png",
        cleanup=True,
    )

    assert ZkProver(circuit).prove()
    assert dequantization(I.data) == dequantization(layers[0][0].data)


def test_circuit_generation_value_numpy_tensor():
    A = np.array(
        [
            [[Value(1), Value(2)], [Value(2), Value(1)]],
            [[Value(1), Value(2)], [Value(2), Value(1)]],
        ]
    )
    B = np.array(
        [
            [[Value(3), Value(4)], [Value(3), Value(4)]],
            [[Value(3), Value(4)], [Value(3), Value(4)]],
        ]
    )
    C = A + B

    circuit, _, layers = Value.compile_layered_circuit(C[0][0][0], True)
    assert len(C) == 2
    assert circuit.size == 3
    draw_dot(layers[0][0]).render(
        "tests/assets/value_numpy_tensor",
        format="png",
        cleanup=True,
    )

    assert ZkProver(circuit).prove()
    assert set(sorted([dequantization(x.data) for x in C[0].flatten()])) == set(
        [x for x in sorted([dequantization(x.data) for x in layers[0]]) if x > 0]
    )


def test_circuit_generation_matrix_multiplication():
    A = np.array([[Value(1.129), Value(2.2)], [Value(2.999), Value(0.5)]])
    B = np.array([Value(-100.12), Value(4)])
    C = A @ B
    circuit, _, layers = Value.compile_layered_circuit(C[0], True)
    draw_dot(C[0]).render(
        "tests/assets/matrix_multiplication", format="png", cleanup=True
    )
    assert circuit.size == 4
    assert ZkProver(circuit).prove()
    assert dequantization(C[0].data) == dequantization(layers[0][0].data)
