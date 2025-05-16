from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

# --- Oracle Construction ---
def create_oracle(n_qubits, marked_state):
    """
    Creates an oracle that marks the solution state with a negative phase.
    Args:
        n_qubits (int): Number of qubits in the circuit
        marked_state (int): The state to mark (in decimal)
    Returns:
        QuantumCircuit: The oracle circuit
    """
    oracle = QuantumCircuit(n_qubits)
    # Convert marked_state to binary string and pad with zeros
    binary_state = format(marked_state, f'0{n_qubits}b')
    # Apply X gates to qubits that are 0 in the marked state
    for qubit, bit in enumerate(binary_state):
        if bit == '0':
            oracle.x(qubit)
    # Apply multi-controlled Z gate (as H-X-mcx-X-H sandwich)
    oracle.h(n_qubits - 1)
    oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    oracle.h(n_qubits - 1)
    # Uncompute X gates
    for qubit, bit in enumerate(binary_state):
        if bit == '0':
            oracle.x(qubit)
    return oracle

# --- Diffusion Operator (Inversion about the mean) ---
def create_diffusion(n_qubits):
    """
    Creates the diffusion operator for Grover's algorithm.
    Args:
        n_qubits (int): Number of qubits in the circuit
    Returns:
        QuantumCircuit: The diffusion circuit
    """
    diffusion = QuantumCircuit(n_qubits)
    # Apply H gates to all qubits
    for qubit in range(n_qubits):
        diffusion.h(qubit)
    # Apply X gates to all qubits
    for qubit in range(n_qubits):
        diffusion.x(qubit)
    # Apply multi-controlled Z gate
    diffusion.h(n_qubits - 1)
    diffusion.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    diffusion.h(n_qubits - 1)
    # Uncompute X gates
    for qubit in range(n_qubits):
        diffusion.x(qubit)
    # Uncompute H gates
    for qubit in range(n_qubits):
        diffusion.h(qubit)
    return diffusion

# --- Core Grover's Algorithm ---
def grovers_algorithm(n_qubits, marked_state, num_iterations=None):
    """
    Runs Grover's algorithm to find the marked state.
    Args:
        n_qubits (int): Number of qubits in the circuit
        marked_state (int): The state to find (in decimal)
        num_iterations (int, optional): Number of Grover iterations. If None, uses optimal number.
    Returns:
        tuple: (circuit, counts) where circuit is the final circuit and counts are the measurement results
    """
    # Calculate optimal number of iterations if not provided
    if num_iterations is None:
        num_iterations = int(np.pi/4 * np.sqrt(2**n_qubits))
    # Create quantum circuit with n_qubits and n classical bits
    qc = QuantumCircuit(n_qubits, n_qubits)
    # Initialize all qubits in superposition
    for qubit in range(n_qubits):
        qc.h(qubit)
    # Apply Grover iterations (oracle + diffusion)
    for _ in range(num_iterations):
        qc.append(create_oracle(n_qubits, marked_state), range(n_qubits))
        qc.append(create_diffusion(n_qubits), range(n_qubits))
    # Measure all qubits
    qc.measure(range(n_qubits), range(n_qubits))
    # Simulate the circuit
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    result = simulator.run(transpiled_qc, shots=1000).result()
    counts = result.get_counts()
    return qc, counts 