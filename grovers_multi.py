__author__ = "Leo Angelo Genota"
__copyright__ = "Copyright (c) 2025 Leo Angelo Genota"
__credits__ = ["Leo Angelo Genota"]

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Leo Angelo Genota"
__email__ = "genota.leo@gmail.com"
__status__ = "Prototype"

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

# --- Multi-Solution Oracle Construction ---
def create_multi_oracle(n_qubits, marked_indices):
    """
    Creates an oracle that marks all solution states in marked_indices with a negative phase.
    Args:
        n_qubits (int): Number of qubits in the circuit
        marked_indices (list of int): The indices to mark
    Returns:
        QuantumCircuit: The oracle circuit
    """
    oracle = QuantumCircuit(n_qubits)
    for idx in marked_indices:
        binary_state = format(idx, f'0{n_qubits}b')
        # Apply X gates to qubits that are 0 in the marked state
        for qubit, bit in enumerate(binary_state):
            if bit == '0':
                oracle.x(qubit)
        # Apply multi-controlled Z gate
        oracle.h(n_qubits - 1)
        oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        oracle.h(n_qubits - 1)
        # Uncompute X gates
        for qubit, bit in enumerate(binary_state):
            if bit == '0':
                oracle.x(qubit)
    return oracle

# --- Diffusion Operator (same as before) ---
def create_diffusion(n_qubits):
    diffusion = QuantumCircuit(n_qubits)
    for qubit in range(n_qubits):
        diffusion.h(qubit)
    for qubit in range(n_qubits):
        diffusion.x(qubit)
    diffusion.h(n_qubits - 1)
    diffusion.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    diffusion.h(n_qubits - 1)
    for qubit in range(n_qubits):
        diffusion.x(qubit)
    for qubit in range(n_qubits):
        diffusion.h(qubit)
    return diffusion

# --- Multi-Solution Grover's Algorithm ---
def grovers_multi_solution_algorithm(n_qubits, marked_indices, num_iterations=None):
    if num_iterations is None:
        # For r solutions, optimal iterations is int(pi/4 * sqrt(N/r))
        r = len(marked_indices)
        num_iterations = int(np.pi/4 * np.sqrt(2**n_qubits / r))
    qc = QuantumCircuit(n_qubits, n_qubits)
    for qubit in range(n_qubits):
        qc.h(qubit)
    for _ in range(num_iterations):
        qc.append(create_multi_oracle(n_qubits, marked_indices), range(n_qubits))
        qc.append(create_diffusion(n_qubits), range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    result = simulator.run(transpiled_qc, shots=1000).result()
    counts = result.get_counts()
    return qc, counts

# --- Multi-Solution Database Search ---
def grovers_multi_solution_search(database, target):
    """
    Uses Grover's algorithm to search for all occurrences of a target value in a database (Python list).
    Args:
        database (list): The list of items to search.
        target: The value to search for in the database.
    Returns:
        tuple: (circuit, counts) where circuit is the final circuit and counts are the measurement results
    """
    n_qubits = int(np.ceil(np.log2(len(database))))
    marked_indices = [i for i, v in enumerate(database) if v == target]
    if not marked_indices:
        raise ValueError(f"Target '{target}' not found in database.")
    print(f"Target '{target}' is at indices {marked_indices}:")
    for idx in marked_indices:
        print(f"  index {idx} (|{format(idx, f'0{n_qubits}b')}⟩)")
    circuit, counts = grovers_multi_solution_algorithm(n_qubits, marked_indices)
    print("\nMeasurement results:")
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        idx = int(state, 2)
        label = database[idx] if idx < len(database) else "(out of range)"
        print(f"|{state}⟩ (index {idx}, '{label}'): {count} times")
    plot_histogram(counts, figsize=(10, 6))
    plt.title(f"Grover's Multi-Solution Search for '{target}'")
    plt.show()
    return circuit, counts 