# HHL Algorithm: Quantum Linear Systems & Matrix Inversion

A complete gate-level implementation of the **Harrow-Hassidim-Lloyd (HHL) algorithm** in Python using **Qiskit**. This project demonstrates solving a $4 \times 4$ linear system $A\vec{x} = \vec{b}$ and reconstructing the matrix inverse $A^{-1}$ through Quantum Phase Estimation (QPE), controlled auxiliary eigenvalue inversion rotations, and complete register uncomputation.

---

## Technical Overview

The HHL algorithm provides up to an exponential speedup over classical algorithms for estimating features of linear systems $A\vec{x} = \vec{b}$ under sparsity and condition number constraints.

This implementation executes the full pipeline:
- **Register Architecture:** Utilizes 6 qubits split into three registers:
  - **Vector Register ($2$ qubits):** Encodes the 4-dimensional input vector state $\vert{}\vec{b}\rangle$.
  - **Clock Register ($3$ qubits):** Carries out Quantum Phase Estimation to resolve eigenvalues $\lambda$ into binary phase values.
  - **Ancilla Register ($1$ qubit):** Receives the conditional non-unitary rotation to enact $1/\lambda$ scaling.
- **Hamiltonian Simulation & Phase Estimation:** Evolves the system under controlled unitary rotations $e^{i A t}$ parameterized by controlled-phase gates ($P$) and two-qubit controlled-$R_{XX}$ interactions, followed by an inverse Quantum Fourier Transform ($\text{IQFT}$)[cite: 9].
- **Controlled Eigenvalue Inversion:** Applies multi-controlled Pauli-$Y$ rotations (`mcry`) with angles $\theta = 2\arcsin(C/\lambda)$ targeting the ancilla to map $\vert{}1\rangle$ onto amplitudes scaled inversely to each eigenvalue[cite: 9].
- **Uncomputation:** Executes forward $\text{QFT}$ and time-reversed Hamiltonian evolution $-e^{i A t}$ on the clock register to disentangle auxiliary clock states from the solution register.
- **Tomographic Inversion Recovery:** Runs the circuit across all four standard computational basis vectors ($\vert{}00\rangle, \vert{}01\rangle, \vert{}10\rangle, \vert{}11\rangle$). Post-selecting on the ancilla success flag $\vert{}1\rangle$ and zeroed clock registers $\vert{}000\rangle$ produces the matrix inverse $A^{-1}$ column-by-column.

---

## Circuit Specifications

- **Total Qubits:** 6 (1 Ancilla + 3 Clock + 2 Data Vector)
- **Target Dimension:** $4 \times 4$ Hermitian matrix
- **Simulation Method:** Qiskit `AerSimulator` statevector backend
- **Success Condition:** Post-selection on $\text{ancilla} = \vert{}1\rangle$ and $\text{clock} = \vert{}000\rangle$

---

## Prerequisites

```bash
pip install qiskit qiskit-aer numpy matplotlib
