from grovers_algorithm import grovers_algorithm
from grovers_multi import grovers_multi_solution_search
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

# --- Database Search Application using Grover's Algorithm ---
def grovers_database_search(database, target):
    """
    Uses Grover's algorithm to search for a target value in a database (Python list).
    Args:
        database (list): The list of items to search.
        target: The value to search for in the database.
    Returns:
        tuple: (circuit, counts) where circuit is the final circuit and counts are the measurement results
    """
    # Calculate the number of qubits needed to index the database
    n_qubits = int(np.ceil(np.log2(len(database))))
    # Find the index of the target in the database
    try:
        marked_index = database.index(target)
    except ValueError:
        raise ValueError(f"Target '{target}' not found in database.")
    print(f"Target '{target}' is at index {marked_index} (|{format(marked_index, f'0{n_qubits}b')}⟩)")
    # Run Grover's algorithm to find the marked index
    circuit, counts = grovers_algorithm(n_qubits, marked_index)
    # Print measurement results with database labels
    print("\nMeasurement results:")
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        idx = int(state, 2)
        label = database[idx] if idx < len(database) else "(out of range)"
        print(f"|{state}⟩ (index {idx}, '{label}'): {count} times")
    # Plot a histogram of the results
    plot_histogram(counts, figsize=(10, 6))
    plt.title(f"Grover's Algorithm Database Search for '{target}'")
    plt.show()
    return circuit, counts

if __name__ == "__main__":
    # Example usage for database search
    database = ["Bob", "Eve", "Mallory", "Trent", "Peggy", "Alice", "Victor", "Alice"]
    target = "Alice"
    # Run the single-solution database search
    print("\n--- Single-Solution Grover's Search ---")
    grovers_database_search(database, target)
    # Run the multi-solution database search
    print("\n--- Multi-Solution Grover's Search ---")
    grovers_multi_solution_search(database, target) 