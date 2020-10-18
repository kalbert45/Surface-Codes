import numpy as np
import cirq
import json

# incomplete, should rely on an input qubit (?)
class LogicalQubit:
	def __init__(self):
		self.qubits = cirq.GridQubit.square(3)

def initQubits(init, qubits):
	if (init == 1):
		for i in range(len(qubits)):
			yield cirq.X(qubits[i])


# given 9 qubits in a grid, returns a Clifford circuit
def surfaceCode(init, q):
	ancilla0 = cirq.NamedQubit('ancilla0')
	ancilla1 = cirq.NamedQubit('ancilla1')
	ancilla2 = cirq.NamedQubit('ancilla2')
	ancilla3 = cirq.NamedQubit('ancilla3')
	ancilla4 = cirq.NamedQubit('ancilla4')
	ancilla5 = cirq.NamedQubit('ancilla5')
	ancilla6 = cirq.NamedQubit('ancilla6')
	ancilla7 = cirq.NamedQubit('ancilla7')

	# X stabilizers: X1X2, X0X1X3X4, X4X5X7X8, X6X7 (H to ancilla, CNOT controlled on ancilla, then H, measure in Z)
	# Z stabilizers: Z0Z3, Z1Z4Z2Z5, Z3Z6Z4Z7, Z5Z8 (ancilla, CNOT gates, then measure in Z)

	# measure stabilizers with repetition to account for measurement error
	circuit = cirq.Circuit(
		# initialize qubits
		initQubits(init, q),

		# inject errors
		cirq.X(q[0]),
		#cirq.Y(q[1]),
		#cirq.Z(q[2]),

		# measure Z stabs
		cirq.CNOT(q[0], ancilla0),
		cirq.CNOT(q[3], ancilla0),
		cirq.measure(ancilla0),

		cirq.CNOT(q[1], ancilla1),
		cirq.CNOT(q[4], ancilla1),
		cirq.CNOT(q[2], ancilla1),
		cirq.CNOT(q[5], ancilla1),
		cirq.measure(ancilla1),

		cirq.CNOT(q[3], ancilla2),
		cirq.CNOT(q[6], ancilla2),
		cirq.CNOT(q[4], ancilla2),
		cirq.CNOT(q[7], ancilla2),
		cirq.measure(ancilla2),

		cirq.CNOT(q[5], ancilla3),
		cirq.CNOT(q[8], ancilla3),
		cirq.measure(ancilla3),


		# measure X stabs
		cirq.H(ancilla4),
		cirq.CNOT(ancilla4, q[1]),
		cirq.CNOT(ancilla4, q[2]),
		cirq.H(ancilla4),
		cirq.measure(ancilla4),

		cirq.H(ancilla5),
		cirq.CNOT(ancilla5, q[0]),
		cirq.CNOT(ancilla5, q[1]),
		cirq.CNOT(ancilla5, q[3]),
		cirq.CNOT(ancilla5, q[4]),
		cirq.H(ancilla5),
		cirq.measure(ancilla5),

		cirq.H(ancilla6),
		cirq.CNOT(ancilla6, q[4]),
		cirq.CNOT(ancilla6, q[5]),
		cirq.CNOT(ancilla6, q[7]),
		cirq.CNOT(ancilla6, q[8]),
		cirq.H(ancilla6),
		cirq.measure(ancilla6),

		cirq.H(ancilla7),
		cirq.CNOT(ancilla7, q[6]),
		cirq.CNOT(ancilla7, q[7]),
		cirq.H(ancilla7),
		cirq.measure(ancilla7)
	)

	return circuit

def getCorrectionGate(q, gate):
	if (gate == "I"):
		return cirq.I(q)
	elif (gate == "X"):
		return cirq.X(q)
	elif (gate == "Y"):
		return cirq.Y(q)
	elif (gate == "Z"):
		return cirq.Z(q)
	else:
		return None

# given qubit, prepare logical qubit
def prepLogicalQubit(init):
	L = LogicalQubit()
	code = surfaceCode(init, L.qubits)

	# run simulator on code
	simulator = cirq.CliffordSimulator()

	# only preps logical 0 for now
	# repeat to account for measurement error (not yet implemented)
	# Use lookup table to find correction
	result = simulator.run(code)

	ancillas = ""
	for i in range(8):
		if (result.measurements['ancilla' + str(i)][0][0]):
			ancillas += "1"
		else:
			ancillas += "0"
		
	print('ancillas: ' + ancillas)

	with open("sf17lookup.json", "r") as read_file:
		correctionLookup = json.load(read_file)
	
	corrections = correctionLookup[ancillas]
	corrections = list(corrections)

	print('corrections: ' + str(corrections))

	# apply correction to qubits in surface code
	correctionCircuit = cirq.Circuit(
		initQubits(init, L.qubits),

		# inject errors again, need to fix
		cirq.X(L.qubits[0]),
		#cirq.Y(L.qubits[1]),
		#cirq.Z(L.qubits[2]),

		getCorrectionGate(L.qubits[0], corrections[0]),
		getCorrectionGate(L.qubits[1], corrections[1]),
		getCorrectionGate(L.qubits[2], corrections[2]),
		getCorrectionGate(L.qubits[3], corrections[3]),
		getCorrectionGate(L.qubits[4], corrections[4]),
		getCorrectionGate(L.qubits[5], corrections[5]),
		getCorrectionGate(L.qubits[6], corrections[6]),
		getCorrectionGate(L.qubits[7], corrections[7]),
		getCorrectionGate(L.qubits[8], corrections[8]),
		cirq.measure(L.qubits[0], key='result0'),
		cirq.measure(L.qubits[1], key='result1'),
		cirq.measure(L.qubits[2], key='result2'),
		cirq.measure(L.qubits[3], key='result3'),
		cirq.measure(L.qubits[4], key='result4'),
		cirq.measure(L.qubits[5], key='result5'),
		cirq.measure(L.qubits[6], key='result6'),
		cirq.measure(L.qubits[7], key='result7'),
		cirq.measure(L.qubits[8], key='result8')
		)

	result = simulator.run(correctionCircuit)

	finalStates = ""
	for i in range(9):
		if (result.measurements['result' + str(i)][0][0]):
			finalStates += "1"
		else:
			finalStates += "0"

	print('data qubit measurements: ' + finalStates)

	# use lookup table to find logical state.
	with open("sf17_zmeas_lookup.json", "r") as read_file:
		stateLookup = json.load(read_file)

	state = int(stateLookup[finalStates])

	return state

def main():
	print('final state 1: ' + str(prepLogicalQubit(1)))
	print('')
	print('final state 0: ' + str(prepLogicalQubit(0)))

if __name__ == '__main__':
    main()