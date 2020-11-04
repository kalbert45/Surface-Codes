import numpy as np
import cirq
import json

# initialize Logical qubits to 0 state. init is number of logical qubits we want.
class LogicalQubits:
	def __init__(self, init):
		assert (init >= 1)
		self.qubits = cirq.GridQubit.rect(init, 9)
		self.gates = initQubits(9, self.qubits)

	# adds gates on the L1, and L2 logical qubit if 2-qubit gate
	def gateOnLogical(self, gate, L1, L2=None):
		if (L2 is None):
			L1 = L1 * 9
			for i in range(9):
				self.gates.append(gate.on(self.qubits[L1 + i]))
		else:
			L1 = L1 * 9
			L2 = L2 * 9
			for i in range(9):
				self.gates.append(gate.on(self.qubits[L1 + i], self.qubits[L2 + i]))

	# L points to logical qubit, index should be 0-8 inclusive and points to data qubit
	def injectError(self, gate, L, index):
		k = L*9 + index
		L.gates.append(gate.on(self.qubits[k]))

def initQubits(size, qubits):
	gates = []
	for i in range(len(qubits)):
		gates.append(cirq.I(qubits[i]))
	return gates

# yields all gates stored in L, also initializes related logical qubits
def initLogicalQubits(L):
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

# given logical qubits and an index pointing to one, returns a Clifford circuit
def surfaceCode(L, i):

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
		initLogicalQubits(L),

		# measure Z stabs
		cirq.CNOT(L.qubits[i+0], ancilla0),
		cirq.CNOT(L.qubits[i+3], ancilla0),
		cirq.measure(ancilla0),

		cirq.CNOT(L.qubits[i+1], ancilla1),
		cirq.CNOT(L.qubits[i+4], ancilla1),
		cirq.CNOT(L.qubits[i+2], ancilla1),
		cirq.CNOT(L.qubits[i+5], ancilla1),
		cirq.measure(ancilla1),

		cirq.CNOT(L.qubits[i+3], ancilla2),
		cirq.CNOT(L.qubits[i+6], ancilla2),
		cirq.CNOT(L.qubits[i+4], ancilla2),
		cirq.CNOT(L.qubits[i+7], ancilla2),
		cirq.measure(ancilla2),

		cirq.CNOT(L.qubits[i+5], ancilla3),
		cirq.CNOT(L.qubits[i+8], ancilla3),
		cirq.measure(ancilla3),


		# measure X stabs
		cirq.H(ancilla4),
		cirq.CNOT(ancilla4, L.qubits[i+1]),
		cirq.CNOT(ancilla4, L.qubits[i+2]),
		cirq.H(ancilla4),
		cirq.measure(ancilla4),

		cirq.H(ancilla5),
		cirq.CNOT(ancilla5, L.qubits[i+0]),
		cirq.CNOT(ancilla5, L.qubits[i+1]),
		cirq.CNOT(ancilla5, L.qubits[i+3]),
		cirq.CNOT(ancilla5, L.qubits[i+4]),
		cirq.H(ancilla5),
		cirq.measure(ancilla5),

		cirq.H(ancilla6),
		cirq.CNOT(ancilla6, L.qubits[i+4]),
		cirq.CNOT(ancilla6, L.qubits[i+5]),
		cirq.CNOT(ancilla6, L.qubits[i+7]),
		cirq.CNOT(ancilla6, L.qubits[i+8]),
		cirq.H(ancilla6),
		cirq.measure(ancilla6),

		cirq.H(ancilla7),
		cirq.CNOT(ancilla7, L.qubits[i+6]),
		cirq.CNOT(ancilla7, L.qubits[i+7]),
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

# given logical qubits and an index pointing to one, return logical state
def measureLogicalQubit(L, index):
	index = index*9
	#init_state = findLogicalStatevector(L)

	code = surfaceCode(L, index)

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
		initLogicalQubits(L),

		getCorrectionGate(L.qubits[index+0], corrections[0]),
		getCorrectionGate(L.qubits[index+1], corrections[1]),
		getCorrectionGate(L.qubits[index+2], corrections[2]),
		getCorrectionGate(L.qubits[index+3], corrections[3]),
		getCorrectionGate(L.qubits[index+4], corrections[4]),
		getCorrectionGate(L.qubits[index+5], corrections[5]),
		getCorrectionGate(L.qubits[index+6], corrections[6]),
		getCorrectionGate(L.qubits[index+7], corrections[7]),
		getCorrectionGate(L.qubits[index+8], corrections[8]),
		cirq.measure(L.qubits[index+0], key='result0'),
		cirq.measure(L.qubits[index+1], key='result1'),
		cirq.measure(L.qubits[index+2], key='result2'),
		cirq.measure(L.qubits[index+3], key='result3'),
		cirq.measure(L.qubits[index+4], key='result4'),
		cirq.measure(L.qubits[index+5], key='result5'),
		cirq.measure(L.qubits[index+6], key='result6'),
		cirq.measure(L.qubits[index+7], key='result7'),
		cirq.measure(L.qubits[index+8], key='result8')
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

	return state


def main():
	# gateOnLogical to apply gates
	# measureLogicalQubit to run circuit and give final state

	# debugging surface code; test 2 and 3 qubit errors (x,y,z)
	# debugging gate on logical; apply multiple gates and make sure final state vector is correct

	L = LogicalQubits(2)
	L.gateOnLogical(cirq.CNOT, 0, 1)
	print('CNOT gate only: 1st qubit state = ' + str(measureLogicalQubit(L, 0)))
	print('2nd qubit state = ' + str(measureLogicalQubit(L, 1)))

	L = LogicalQubits(2)
	L.gateOnLogical(cirq.X, 0)
	L.gateOnLogical(cirq.CNOT, 0, 1)
	print('Flip first then CNOT gate: 1st qubit state = ' + str(measureLogicalQubit(L, 0)))
	print('2nd qubit state = ' + str(measureLogicalQubit(L, 1)))

	L = LogicalQubits(2)
	L.gateOnLogical(cirq.X, 1)
	L.gateOnLogical(cirq.CNOT, 0, 1)
	print('Flip second then CNOT gate: 1st qubit state = ' + str(measureLogicalQubit(L, 0)))
	print('2nd qubit state = ' + str(measureLogicalQubit(L, 1)))


	print('desired outcome:')
	q0 = cirq.NamedQubit('test0')
	q1 = cirq.NamedQubit('test1')
	circuit = cirq.Circuit(cirq.X(q0), cirq.CNOT(q0, q1), cirq.measure(q0), cirq.measure(q1))
	simulator = cirq.CliffordSimulator()
	result = simulator.run(circuit)
	if (result.measurements['test0'][0][0]):
		print("q0: 1")
	else:
		print("q0: 0")

	if (result.measurements['test1'][0][0]):
		print("q1: 1")
	else:
		print("q1: 0")

if __name__ == '__main__':
    main()