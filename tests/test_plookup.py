import random
from zerok.lookup.plookup.setup import Setup
from zerok.lookup.plookup.program import Params
from zerok.lookup.plookup.prover import Prover, Proof
from zerok.lookup.plookup.verifier import Verifier


# setup: public setup includes srs
# public_table: public table
# witness: values to lookup
def prover(setup: Setup, params: Params, witness: list[int]):
    prover = Prover(setup, params)
    return prover.prove(witness)


def prover_simple_array(setup: Setup, params: Params):
    # values to lookup
    witness = [1, 1, 5, 5, 6, 6, 5]  # twinkle twinkle little star
    proof = prover(setup, params, witness)
    return proof


def prover_random_lookup(setup: Setup, params: Params, size: int):
    # values to lookup
    witness = []
    for _ in range(size):
        witness.append(random.randint(1, size))

    proof = prover(setup, params, witness)
    return proof


def verifier(setup: Setup, params: Params, proof: Proof):
    print("Beginning verifier test")
    verifier = Verifier(setup, params)
    return verifier.verify(proof)


def test_plookup_random_values():
    size = 4
    # random number, normally comes from MPC(Multi-Party Computation)
    tau = 100

    # public table
    # table = [1...size]
    table = []
    for i in range(1, size + 1):
        table.append(i)

    group_order_N = len(table)
    # number of powers of tau
    powers = group_order_N * 3
    # do setup
    setup = Setup(powers, tau)
    # set public params
    params = Params(table)
    # run prover
    proof = prover_random_lookup(setup, params, 2)
    # run verifier
    return verifier(setup, params, proof)
