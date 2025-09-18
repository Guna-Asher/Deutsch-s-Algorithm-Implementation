from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import numpy as np

def deutsch_algorithm(oracle_type):
    """
    Implements Deutsch's Algorithm to determine if a function f: {0,1} -> {0,1} is constant or balanced.

    Args:
    oracle_type (str): Type of oracle - 'constant_0', 'constant_1', 'balanced_01', 'balanced_10'

    Returns:
    dict: Measurement results
    """
    # Create a quantum circuit with 2 qubits and 1 classical bit
    qc = QuantumCircuit(2, 1)

    # Initialize the second qubit to |1>
    qc.x(1)

    # Apply Hadamard gates to both qubits for superposition
    qc.h(0)
    qc.h(1)

    # Apply the oracle based on the function type
    if oracle_type == 'constant_0':
        # f(0) = 0, f(1) = 0: No gates needed
        pass
    elif oracle_type == 'constant_1':
        # f(0) = 1, f(1) = 1: Apply X gate to second qubit
        qc.x(1)
    elif oracle_type == 'balanced_01':
        # f(0) = 0, f(1) = 1: Apply CNOT gate
        qc.cx(0, 1)
    elif oracle_type == 'balanced_10':
        # f(0) = 1, f(1) = 0: Apply X to second qubit, then CNOT, then X again
        qc.x(1)
        qc.cx(0, 1)
        qc.x(1)
    else:
        raise ValueError("Invalid oracle type")

    # Apply Hadamard gate to the first qubit
    qc.h(0)

    # Measure the first qubit
    qc.measure(0, 0)

    # Simulate the circuit
    simulator = Aer.get_backend('qasm_simulator')
    result = simulator.run(qc, shots=1024).result()
    counts = result.get_counts(qc)

    return counts

def interpret_result(counts):
    """
    Interprets the measurement results.

    Args:
    counts (dict): Measurement counts

    Returns:
    str: 'constant' or 'balanced'
    """
    # If '0' is measured, function is constant; if '1', balanced
    if '0' in counts and counts['0'] > counts.get('1', 0):
        return 'constant'
    else:
        return 'balanced'

# Test the algorithm with different oracles
if __name__ == "__main__":
    oracle_types = ['constant_0', 'constant_1', 'balanced_01', 'balanced_10']

    for oracle in oracle_types:
        print(f"\nTesting oracle: {oracle}")
        counts = deutsch_algorithm(oracle)
        result = interpret_result(counts)
        print(f"Measurement counts: {counts}")
        print(f"Function is: {result}")

        # Plot histogram (optional, for visualization)
        plot_histogram(counts)
        plt.title(f"Measurement Results for {oracle}")
        plt.savefig(f'{oracle}_histogram.png')
        plt.close()

    # Thorough testing: Noise model
    print("\n--- Testing with Noise Model ---")
    noise_model = NoiseModel()
    error = depolarizing_error(0.01, 1)  # 1% error on single qubits
    noise_model.add_all_qubit_quantum_error(error, ['h', 'x'])

    for oracle in oracle_types:
        qc = QuantumCircuit(2, 1)
        qc.x(1)
        qc.h(0)
        qc.h(1)
        # Add oracle
        if oracle == 'constant_0':
            pass
        elif oracle == 'constant_1':
            qc.x(1)
        elif oracle == 'balanced_01':
            qc.cx(0, 1)
        elif oracle == 'balanced_10':
            qc.x(1)
            qc.cx(0, 1)
            qc.x(1)
        qc.h(0)
        qc.measure(0, 0)

        simulator = Aer.get_backend('qasm_simulator')
        result = simulator.run(qc, noise=noise_model, shots=1024).result()
        counts = result.get_counts(qc)
        result_type = interpret_result(counts)
        print(f"Noisy {oracle}: {result_type} (counts: {counts})")

    # Performance testing: Multiple runs
    print("\n--- Performance Testing ---")
    runs = 100
    success_rate = {}
    for oracle in oracle_types:
        correct = 0
        expected = 'constant' if 'constant' in oracle else 'balanced'
        for _ in range(runs):
            counts = deutsch_algorithm(oracle)
            if interpret_result(counts) == expected:
                correct += 1
        success_rate[oracle] = correct / runs * 100
        print(f"{oracle}: {success_rate[oracle]:.1f}% success rate")

    # Deutsch-Jozsa Algorithm for n=3 qubits
    print("\n--- Deutsch-Jozsa Algorithm (n=3) ---")
    def deutsch_jozsa_oracle(qc, oracle_type, n):
        if oracle_type == 'constant_0':
            pass  # All f(x) = 0
        elif oracle_type == 'constant_1':
            qc.x(n)  # All f(x) = 1
        elif oracle_type == 'balanced':
            # Balanced: f(x) = x[0] (first bit)
            qc.cx(0, n)

    def deutsch_jozsa(n, oracle_type):
        qc = QuantumCircuit(n+1, n)
        qc.x(n)
        for i in range(n+1):
            qc.h(i)
        deutsch_jozsa_oracle(qc, oracle_type, n)
        for i in range(n):
            qc.h(i)
        qc.measure(list(range(n)), list(range(n)))
        simulator = Aer.get_backend('qasm_simulator')
        result = simulator.run(qc, shots=1024).result()
        counts = result.get_counts(qc)
        return counts

    dj_oracles = ['constant_0', 'constant_1', 'balanced']
    for oracle in dj_oracles:
        counts = deutsch_jozsa(3, oracle)
        # If all measurements are 0, constant; else balanced
        is_constant = all(key == '0'*3 for key in counts.keys())
        print(f"DJ {oracle}: {'constant' if is_constant else 'balanced'}")
