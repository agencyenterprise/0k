mod zerok_compiler;
use zerok_compiler::zerok_backend::executor;
extern crate serde as serde_crate;
use expander_compiler::frontend::internal::Serde;
use halo2curves::{bn256::Fr, ff::FromUniformBytes};
use serde_crate::Deserialize;
use serde_json;
#[derive(Debug, Deserialize)]
#[serde(rename_all = "lowercase")]
enum Expression {
    Operation {
        op: Operation,
        left: Box<Expression>,
        right: Box<Expression>,
    },
    Const {
        const_value: u32,
    },
    Var {
        var: u32,
    },
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "lowercase")]
enum Operation {
    Add,
    Mul,
}

use expander_compiler::frontend::*; // Import the Serde trait

fn deserialize_dag(builder: &mut API<BN254Config>, x: &[Variable], expr: &Expression) -> Variable {
    match expr {
        Expression::Operation { op, left, right } => {
            let left_var = deserialize_dag(builder, x, left);
            let right_var = deserialize_dag(builder, x, right);

            match op {
                Operation::Add => builder.add(left_var, right_var),
                Operation::Mul => builder.mul(left_var, right_var),
            }
        }
        Expression::Const { const_value } => {
            builder.constant(BN254::from(*const_value as u64)) // Add a constant
        }
        Expression::Var { var } => {
            x[*var as usize] // Reference the variable (e.g., x[0] or x[1])
        }
    }
}

declare_circuit!(Circuit {
    sum: PublicVariable,
    x: [Variable; 4],
});

impl Define<BN254Config> for Circuit<Variable> {
    fn define(&self, builder: &mut API<BN254Config>) {
        // Define the JSON input representing the DAG
        let json_dag = r#"
        {
            "operation": {
                "op": "add",
                "left": {
                    "operation": {
                        "op": "add",
                        "left": {
                            "var": {
                                "var": 0
                            }
                        },
                        "right": {
                            "var": {
                                "var": 1
                            }
                        }
                    }
                },
                "right": {
                    "const": {
                        "const_value": 2
                    }
                }
            }
        }
        "#;
        let parsed_dag: Expression = match serde_json::from_str(json_dag) {
            Ok(dag) => {
                println!("Parsed DAG: {:?}", dag);
                dag
            }
            Err(e) => panic!("Failed to parse JSON DAG: {}", e),
        };
        // Use the deserialized DAG to build the circuit
        let sum = deserialize_dag(builder, &self.x, &parsed_dag);

        // Assert that the computed sum equals the expected public value
        builder.assert_is_equal(sum, self.sum);
    }
}

fn bigint_to_fr(u256_value: &str) -> Fr {
    // Convert the U256 to a BigUint (num-bigint's large number representation)
    let large_number = num_bigint::BigUint::parse_bytes(u256_value.as_bytes(), 10).unwrap();

    // Initialize a 64-byte array
    let mut bytes = [0u8; 64];

    // Convert the BigUint into a byte array in little-endian order
    let large_bytes = large_number.to_bytes_le();

    // Copy the bytes into the 64-byte array
    bytes[..large_bytes.len()].copy_from_slice(&large_bytes);

    // Call the `from_uniform_bytes` function to convert the bytes into Fr
    Fr::from_uniform_bytes(&bytes)
}
fn main() {
    let compile_result = compile(&Circuit::default()).unwrap();
    let assignment = Circuit::<BN254> {
        sum: BN254::from(bigint_to_fr("4")),
        x: [
            BN254::from(bigint_to_fr("1")),
            BN254::from(bigint_to_fr("1")),
            BN254::from(bigint_to_fr("2")),
            BN254::from(bigint_to_fr("4")),
        ],
    };

    let witness = compile_result
        .witness_solver
        .solve_witness(&assignment)
        .unwrap();
    let output = compile_result.layered_circuit.run(&witness);
    print!("OUTPUT: {:?}", output);
    assert_eq!(output, vec![true]);

    let file = std::fs::File::create("circuit.txt").unwrap();
    let writer = std::io::BufWriter::new(file);
    compile_result
        .layered_circuit
        .serialize_into(writer)
        .unwrap();

    let file = std::fs::File::create("witness.txt").unwrap();
    let writer = std::io::BufWriter::new(file);
    witness.serialize_into(writer).unwrap();

    let file = std::fs::File::create("witness_solver.txt").unwrap();
    let writer = std::io::BufWriter::new(file);
    compile_result
        .witness_solver
        .serialize_into(writer)
        .unwrap();
    executor();
}
