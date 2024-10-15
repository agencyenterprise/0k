use std::panic;
use std::panic::AssertUnwindSafe;
use std::time::Instant;

use arith::Field;
use expander_circuit::Circuit;
use expander_config::GKRConfig;
use expander_config::{root_println, BN254ConfigKeccak, Config, FieldType, GKRScheme, MPIConfig};
use gkr::{Prover, Verifier};
use rand::Rng;
use sha2::Digest;

pub fn executor() {
    let mpi_config = MPIConfig::new();

    test_gkr_bn254_keccak_helper::<BN254ConfigKeccak>(&Config::<BN254ConfigKeccak>::new(
        GKRScheme::Vanilla,
        mpi_config.clone(),
    ));

    MPIConfig::finalize();
}

fn test_gkr_bn254_keccak_helper<C: GKRConfig>(config: &Config<C>) {
    root_println!(config.mpi_config, "============== start ===============");
    root_println!(config.mpi_config, "Field Type: {:?}", C::FIELD_TYPE);
    let circuit_copy_size: usize = match C::FIELD_TYPE {
        FieldType::BN254 => 2,
        _ => unreachable!(),
    };
    root_println!(
        config.mpi_config,
        "Proving {} keccak instances at once.",
        circuit_copy_size * C::get_field_pack_size()
    );
    root_println!(config.mpi_config, "Config created.");

    let circuit_path = "./circuit.txt";
    let mut circuit = Circuit::<C>::load_circuit(circuit_path);
    root_println!(config.mpi_config, "Circuit loaded.");

    let witness_path = "./witness.txt";
    circuit.load_witness_file(witness_path);
    root_println!(config.mpi_config, "Witness loaded.");

    circuit.evaluate();
    let output = &circuit.layers.last().unwrap().output_vals;
    assert!(output[..circuit.expected_num_output_zeros]
        .iter()
        .all(|f| f.is_zero()));

    let mut prover = Prover::new(config);
    prover.prepare_mem(&circuit);

    let proving_start = Instant::now();
    let (claimed_v, proof) = prover.prove(&mut circuit);
    root_println!(
        config.mpi_config,
        "Proving time: {} μs",
        proving_start.elapsed().as_micros()
    );

    root_println!(
        config.mpi_config,
        "Proof generated. Size: {} bytes",
        proof.bytes.len()
    );
    root_println!(config.mpi_config, "Proof bytes: ");
    proof.bytes.iter().take(16).for_each(|b| print!("{} ", b));
    print!("... ");
    proof
        .bytes
        .iter()
        .rev()
        .take(16)
        .rev()
        .for_each(|b| print!("{} ", b));
    root_println!(config.mpi_config,);

    root_println!(config.mpi_config, "Proof hash: ");
    sha2::Sha256::digest(&proof.bytes)
        .iter()
        .for_each(|b| print!("{} ", b));
    root_println!(config.mpi_config,);

    let mut public_input_gathered = if config.mpi_config.is_root() {
        vec![C::SimdCircuitField::ZERO; circuit.public_input.len() * config.mpi_config.world_size()]
    } else {
        vec![]
    };
    config
        .mpi_config
        .gather_vec(&circuit.public_input, &mut public_input_gathered);

    // Verify
    if config.mpi_config.is_root() {
        let verifier = Verifier::new(config);
        println!("Verifier created.");
        let verification_start = Instant::now();
        assert!(verifier.verify(&mut circuit, &public_input_gathered, &claimed_v, &proof));
        println!(
            "Verification time: {} μs",
            verification_start.elapsed().as_micros()
        );
        println!("Correct proof verified.");

        let mut bad_proof = proof.clone();
        let rng = &mut rand::thread_rng();
        let random_idx = rng.gen_range(0..bad_proof.bytes.len());
        let random_change = rng.gen_range(1..256) as u8;
        bad_proof.bytes[random_idx] ^= random_change;

        let result = panic::catch_unwind(AssertUnwindSafe(|| {
            verifier.verify(&mut circuit, &public_input_gathered, &claimed_v, &bad_proof)
        }));

        let final_result = result.unwrap_or_default();

        assert!(!final_result);
        println!("Bad proof rejected.");
        println!("============== end ===============");
    }
}
