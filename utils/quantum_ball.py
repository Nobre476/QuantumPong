from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.compiler import transpile
import numpy as np

def quantum_decision():
    """Cria uma decisão quântica aleatória (0 ou 1)"""
    qc = QuantumCircuit(1, 1)  # 1 qubit, 1 bit clássico
    qc.h(0)  # Aplica porta Hadamard (superposição)
    qc.measure(0, 0)  # Mede o qubit

    backend = Aer.get_backend('qasm_simulator')
    compiled_circuit = transpile(qc, backend)
    result = backend.run(compiled_circuit, shots=1).result()
    return int(result.get_counts().most_frequent())
