import numpy as np
import cirq
import json

# initialize Logical qubit, init should be 0 or 1
class LogicalQubit:
	def __init__(self, init):
		self.qubits = cirq.GridQubit.square(3)
		self.gates = initQubits(init, self.qubits)

def initQubits(init, qubits):
	gates = []
	if (init == 1):
		for i in range(len(qubits)):
			gates.append(cirq.X(qubits[i]))
		return gates
	else:
		for i in range(len(qubits)):
			gates.append(cirq.I(qubits[i]))
		return gates

# adds gates for all 9 data qubits (not tested)
def gateOnLogical(gate, L):
	for i in range(len(L.qubits)):
		L.gates.append(gate.on(L.qubits[i]))

# index should be 0-8 inclusive
def injectError(gate, L, index):
	L.gates.append(gate.on(L.qubits[index]))

# yields all gates stored in L
def initLogicalQubit(L):
	for i in range(len(L.gates)):
		yield L.gates[i]

# WIP
# finds state vector for initializing logical qubit
#def findLogicalStatevector(L):
	#ancilla0 = cirq.NamedQubit('ancilla0')
#	ancilla1 = cirq.NamedQubit('ancilla1')
#	ancilla2 = cirq.NamedQubit('ancilla2')
#	ancilla3 = cirq.NamedQubit('ancilla3')
#	ancilla4 = cirq.NamedQubit('ancilla4')
#	ancilla5 = cirq.NamedQubit('ancilla5')
#	ancilla6 = cirq.NamedQubit('ancilla6')
#	ancilla7 = cirq.NamedQubit('ancilla7')

#	circuit = cirq.Circuit(
	#	cirq.I(ancilla0),
#		cirq.I(ancilla1),
#		cirq.I(ancilla2),
#		cirq.I(ancilla3),
#		cirq.I(ancilla4),
#		cirq.I(ancilla5),
#		cirq.I(ancilla6),
#		cirq.I(ancilla7),
#		initLogicalQubit(L)
#		)

	#simulator = cirq.DensityMatrixSimulator()
	#result = simulator.simulate(circuit)

	#print(result.final_density_matrix)

	#return np.array([0,0,0,0])

# given 9 qubits in a grid, returns a Clifford circuit
def surfaceCode(L):
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
		initLogicalQubit(L),

		# measure Z stabs
		cirq.CNOT(L.qubits[0], ancilla0),
		cirq.CNOT(L.qubits[3], ancilla0),
		cirq.measure(ancilla0),

		cirq.CNOT(L.qubits[1], ancilla1),
		cirq.CNOT(L.qubits[4], ancilla1),
		cirq.CNOT(L.qubits[2], ancilla1),
		cirq.CNOT(L.qubits[5], ancilla1),
		cirq.measure(ancilla1),

		cirq.CNOT(L.qubits[3], ancilla2),
		cirq.CNOT(L.qubits[6], ancilla2),
		cirq.CNOT(L.qubits[4], ancilla2),
		cirq.CNOT(L.qubits[7], ancilla2),
		cirq.measure(ancilla2),

		cirq.CNOT(L.qubits[5], ancilla3),
		cirq.CNOT(L.qubits[8], ancilla3),
		cirq.measure(ancilla3),


		# measure X stabs
		cirq.H(ancilla4),
		cirq.CNOT(ancilla4, L.qubits[1]),
		cirq.CNOT(ancilla4, L.qubits[2]),
		cirq.H(ancilla4),
		cirq.measure(ancilla4),

		cirq.H(ancilla5),
		cirq.CNOT(ancilla5, L.qubits[0]),
		cirq.CNOT(ancilla5, L.qubits[1]),
		cirq.CNOT(ancilla5, L.qubits[3]),
		cirq.CNOT(ancilla5, L.qubits[4]),
		cirq.H(ancilla5),
		cirq.measure(ancilla5),

		cirq.H(ancilla6),
		cirq.CNOT(ancilla6, L.qubits[4]),
		cirq.CNOT(ancilla6, L.qubits[5]),
		cirq.CNOT(ancilla6, L.qubits[7]),
		cirq.CNOT(ancilla6, L.qubits[8]),
		cirq.H(ancilla6),
		cirq.measure(ancilla6),

		cirq.H(ancilla7),
		cirq.CNOT(ancilla7, L.qubits[6]),
		cirq.CNOT(ancilla7, L.qubits[7]),
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

# given logical qubit, return logical state
def measureLogicalQubit(L):
	#init_state = findLogicalStatevector(L)

	code = surfaceCode(L)

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
		
	#print('ancillas: ' + ancillas)

	with open("sf17lookup.json", "r") as read_file:
		correctionLookup = json.load(read_file)
	
	corrections = correctionLookup[ancillas]
	corrections = list(corrections)

	#print('corrections: ' + str(corrections))

	# apply correction to qubits in surface code
	correctionCircuit = cirq.Circuit(
		initLogicalQubit(L),

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

	#print('data qubit measurements: ' + finalStates)

	# use lookup table to find logical state.
	with open("sf17_zmeas_lookup.json", "r") as read_file:
		stateLookup = json.load(read_file)

	state = int(stateLookup[finalStates])

	# measurement destroys data
	L.gates = []

	return state


def main():
	# gateOnLogical to apply gates
	# measureLogicalQubit to run circuit and give final state

	# debugging surface code; test 2 and 3 qubit errors (x,y,z)
	# debugging gate on logical; apply multiple gates and make sure final state vector is correct

	L = LogicalQubit(1)
	print('final state 1: ' + str(measureLogicalQubit(L)))
	print()

	L = LogicalQubit(0)
	print('final state 0: ' + str(measureLogicalQubit(L)))


if __name__ == '__main__':
    main()