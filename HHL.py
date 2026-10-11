#imports
from qiskit import transpile, QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.circuit.library import QFT, RXXGate #MCXVGate
from qiskit.visualization import plot_histogram
import numpy as np

#for 4x4 matrix we need 6 qubits: vector register (2 qubits) + clock register (3 qubits) + ancilla register (1 qubit)
ancilla = QuantumRegister(1, 'ancilla')
clock = QuantumRegister(3, 'clock')      # Extracts the eigenvalues
vector = QuantumRegister(2, 'b_vector')  # Holds my data
measurement = ClassicalRegister(1, 'measure_ancilla')

qc1 = QuantumCircuit(ancilla, clock, vector, measurement)
qc2 = QuantumCircuit(ancilla, clock, vector, measurement)
qc3 = QuantumCircuit(ancilla, clock, vector, measurement)
qc4 = QuantumCircuit(ancilla, clock, vector, measurement)

t0 = np.pi / 4

#STATE PREPARATION
qc2.x(vector[0])
qc3.x(vector[1])
qc4.x(vector)

qc1.barrier()
qc2.barrier()
qc3.barrier()
qc4.barrier()

#DECOMPOSITION (Phase Estimation)
qc1.h(clock)
qc2.h(clock)
qc3.h(clock)
qc4.h(clock)

for c in range(3):
    t = t0 * (2 ** c)
    qc1.p(2 * t, clock[c])
    qc2.p(2 * t, clock[c])
    qc3.p(2 * t, clock[c])
    qc4.p(2 * t, clock[c])
    rxx_gate = RXXGate(-2 * t)
    crxx_gate = rxx_gate.control(1)
    qc1.append(crxx_gate, [clock[c], vector[0], vector[1]])
    qc2.append(crxx_gate, [clock[c], vector[0], vector[1]])
    qc3.append(crxx_gate, [clock[c], vector[0], vector[1]])
    qc4.append(crxx_gate, [clock[c], vector[0], vector[1]])

iqft_gate = QFT(num_qubits=3, inverse=True, name="IQFT").to_gate()
qc1.append(iqft_gate, clock)
qc2.append(iqft_gate, clock)
qc3.append(iqft_gate, clock)
qc4.append(iqft_gate, clock)
    
#for test matrix eigenvalues are 1 and 3, we will choose c=smallest eigenvalue
C = 1.0
circuits = [qc1, qc2, qc3, qc4]

for state in range(8):
    if state == 0 or (C / state) > 1.0:
        continue
    
    theta = 2 * np.arcsin(C / state)
    reversed_binary = format(state, '03b')[::-1]
    
    for qc in circuits:
        # Mask the 0s
        for i, bit in enumerate(reversed_binary):
            if bit == '0':
                qc.x(clock[i])
                
        # Apply the rotation
        qc.mcry(theta, clock, ancilla)
        
        # Unmask the 0s
        for i, bit in enumerate(reversed_binary):
            if bit == '0':
                qc.x(clock[i])

#UNCOMPUTATION
qft_gate = QFT(num_qubits=3, inverse=False, name="QFT").to_gate()
qc1.append(qft_gate, clock)
qc2.append(qft_gate, clock)
qc3.append(qft_gate, clock)
qc4.append(qft_gate, clock)

for c in range(3):
    t = -(t0 * (2 ** c)) #reverse time
    qc1.p(2 * t, clock[c])
    qc2.p(2 * t, clock[c])
    qc3.p(2 * t, clock[c])
    qc4.p(2 * t, clock[c])
    rxx_gate = RXXGate(-2 * t)
    crxx_gate = rxx_gate.control(1)
    qc1.append(crxx_gate, [clock[c], vector[0], vector[1]])
    qc2.append(crxx_gate, [clock[c], vector[0], vector[1]])
    qc3.append(crxx_gate, [clock[c], vector[0], vector[1]])
    qc4.append(crxx_gate, [clock[c], vector[0], vector[1]])

qc1.h(clock)
qc2.h(clock)
qc3.h(clock)
qc4.h(clock)

#MEASUREMENT
# qc1.measure(ancilla, measurement)
# qc2.measure(ancilla, measurement)
# qc3.measure(ancilla, measurement)
# qc4.measure(ancilla, measurement)

qc1.save_statevector()
qc2.save_statevector()
qc3.save_statevector()
qc4.save_statevector()

# qc1.draw(output='mpl', filename='HHL_Abstract_Circuit.png', style='clifford')

simulator = AerSimulator(method='statevector')
qc1 = transpile(qc1, simulator)
job = simulator.run(qc1, shots=1)
result1 = job.result()
statevector1 = np.asarray(result1.data(0)['statevector'])

qc2 = transpile(qc2, simulator)
job = simulator.run(qc2, shots=1)
result2 = job.result()
statevector2 = np.asarray(result2.data(0)['statevector'])

qc3 = transpile(qc3, simulator)
job = simulator.run(qc3, shots=1)
result3 = job.result()
statevector3 = np.asarray(result3.data(0)['statevector'])

qc4 = transpile(qc4, simulator)
job = simulator.run(qc4, shots=1)
result4 = job.result()
statevector4 = np.asarray(result4.data(0)['statevector'])

success_amplitude1 = []
success_amplitude2 = []
success_amplitude3 = []
success_amplitude4 = []

for i, amplitude in enumerate(statevector1):
    state_bin = format(i, '06b')
    
    ancilla_bit = state_bin[5]
    clock_bits = state_bin[2:5]
    vector_bits = state_bin[0:2]
    
    if ancilla_bit == '1' and clock_bits == '000':
        success_amplitude1.append((vector_bits, amplitude))

for i, amplitude in enumerate(statevector2):
    state_bin = format(i, '06b')
    
    ancilla_bit = state_bin[5]
    clock_bits = state_bin[2:5]
    vector_bits = state_bin[0:2]
    
    if ancilla_bit == '1' and clock_bits == '000':
        success_amplitude2.append((vector_bits, amplitude))

for i, amplitude in enumerate(statevector3):
    state_bin = format(i, '06b')
    
    ancilla_bit = state_bin[5]
    clock_bits = state_bin[2:5]
    vector_bits = state_bin[0:2]
    
    if ancilla_bit == '1' and clock_bits == '000':
        success_amplitude3.append((vector_bits, amplitude))

for i, amplitude in enumerate(statevector4):
    state_bin = format(i, '06b')
    
    ancilla_bit = state_bin[5]
    clock_bits = state_bin[2:5]
    vector_bits = state_bin[0:2]
    
    if ancilla_bit == '1' and clock_bits == '000':
        success_amplitude4.append((vector_bits, amplitude))

#Normalize
# total_prob1 = sum(abs(amp)**2 for _, amp in success_amplitude1)
# total_prob2 = sum(abs(amp)**2 for _, amp in success_amplitude2)
# total_prob3 = sum(abs(amp)**2 for _, amp in success_amplitude3)
# total_prob4 = sum(abs(amp)**2 for _, amp in success_amplitude4)

# col1 = [amp / np.sqrt(total_prob1) for _, amp in success_amplitude1]
# col2 = [amp / np.sqrt(total_prob2) for _, amp in success_amplitude2]
# col3 = [amp / np.sqrt(total_prob3) for _, amp in success_amplitude3]
# col4 = [amp / np.sqrt(total_prob4) for _, amp in success_amplitude4]

col1 = [amp for _, amp in success_amplitude1]
col2 = [amp for _, amp in success_amplitude2]
col3 = [amp for _, amp in success_amplitude3]
col4 = [amp for _, amp in success_amplitude4]

#Visualize
A_inverse = np.column_stack((col1, col2, col3, col4))
np.set_printoptions(precision=4, suppress=True, linewidth=100)
A_inverse = np.real(A_inverse)
print(qc1.draw())
print(A_inverse)