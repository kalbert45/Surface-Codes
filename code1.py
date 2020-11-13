import numpy as np
import cirq
import json

def chain_error(q1, q2, d1, d2, alpha, diff_chain=False):
	if (diff_chain):
		error_prob = alpha * (pow(d1, 3) + pow(d2, 3))
	else:
		error_prob = alpha * pow(np.abs(d1-d2), 3)

	if (np.random.uniform(0, 1) < error_prob):
		#print('chain error occurred')
		yield cirq.Z(q1)
		yield cirq.X(q2)


# initialize Logical qubits to 0 state. init is number of logical qubits we want.
class LogicalQubits:
	def __init__(self, init, alpha=None, pdark=None, error_model=False):
		assert (init >= 1)
		self.size = 9
		self.qubits = cirq.GridQubit.rect(init, self.size+8)
		self.ancillas = initAncillas(8, self.size, init, self)
		self.gates = initQubits(self.size, self.qubits)
		self.error_model = error_model
		self.alpha = alpha
		self.pdark = pdark

	# i points to logical qubit, j points to data or ancilla
	def qubit(self, i, j):
		i *= 9
		return self.qubits[i + j]

	# adds gates on the L1, and L2 logical qubit if 2-qubit gate
	def gateOnLogical(self, gate, L1, L2=None):
		assert (L1 != L2)
		if (L2 is None):
			for i in range(9):
				self.gates.append(gate.on(self.qubit(L1, i)))
		else:
			if (self.error_model):
				for i in range(9):
					#p dark error
					if (np.random.uniform(0,1) < self.pdark):
						if (np.random.uniform(0,1) < 0.5):
							continue
						else:
							self.gates.append(cirq.CZ.on(self.qubit(L1, i), self.qubit(L2, i)))
					else:
						self.gates.append(gate.on(self.qubit(L1, i), self.qubit(L2, i)))

					# chain specific error
					self.gates.append(chain_error(self.qubit(L1, i), self.qubit(L2, i), i, i, self.alpha, True))
			else:
				for i in range(9):
					self.gates.append(gate.on(self.qubit(L1, i), self.qubit(L2, i)))


	# L points to logical qubit, index should be 0-8 inclusive and points to data qubit
	def injectError(self, gate, L, index):
		L.gates.append(gate.on(self.qubit(L, index)))

# creates 2d list for ancillas
def initAncillas(num_ancillas, num_qubits, num_logical, qubits):
	ancillas = [[None]*num_ancillas]*num_logical 
	for i in range(num_logical):
		for j in range(num_ancillas):
			ancillas[i][j] = qubits.qubit(i, num_qubits+j)
	return ancillas

# returns list of identity gates
def initQubits(size, qubits):
	gates = []
	for i in range(len(qubits)):
		gates.append(cirq.I(qubits[i]))
	return gates

# yields all gates stored in L, also initializes related logical qubits
def initLogicalQubits(L):
	for i in range(len(L.gates)):
		yield L.gates[i]

# given logical qubits and an index pointing to one, returns a Clifford circuit
# implement mapping algorithm here (?)
def surfaceCode(L, i):

	# X stabilizers: X1X2, X0X1X3X4, X4X5X7X8, X6X7 (H to ancilla, CNOT controlled on ancilla, then H, measure in Z)
	# Z stabilizers: Z0Z3, Z1Z4Z2Z5, Z3Z6Z4Z7, Z5Z8 (ancilla, CNOT gates, then measure in Z)

	# measure stabilizers with repetition to account for measurement error

	# no error circuit
	if (L.error_model):
		circuit = cirq.Circuit(
			initLogicalQubits(L),

			# measure Z stabs
			cirq.CNOT(L.qubit(i, 0), L.ancillas[i][0]),
			chain_error(L.qubit(i, 0), L.ancillas[i][0], 0, 9, L.alpha),
			cirq.CNOT(L.qubit(i, 3), L.ancillas[i][0]),
			chain_error(L.qubit(i, 3), L.ancillas[i][0], 3, 9, L.alpha),
			cirq.measure(L.ancillas[i][0], key='ancilla0'),

			cirq.CNOT(L.qubit(i, 1), L.ancillas[i][1]),
			chain_error(L.qubit(i, 1), L.ancillas[i][1], 1, 10, L.alpha),
			cirq.CNOT(L.qubit(i, 4), L.ancillas[i][1]),
			chain_error(L.qubit(i, 4), L.ancillas[i][1], 4, 10, L.alpha),
			cirq.CNOT(L.qubit(i, 2), L.ancillas[i][1]),
			chain_error(L.qubit(i, 2), L.ancillas[i][1], 2, 10, L.alpha),
			cirq.CNOT(L.qubit(i, 5), L.ancillas[i][1]),
			chain_error(L.qubit(i, 5), L.ancillas[i][1], 5, 10, L.alpha),
			cirq.measure(L.ancillas[i][1], key='ancilla1'),

			cirq.CNOT(L.qubit(i, 3), L.ancillas[i][2]),
			chain_error(L.qubit(i, 3), L.ancillas[i][2], 3, 11, L.alpha),
			cirq.CNOT(L.qubit(i, 6), L.ancillas[i][2]),
			chain_error(L.qubit(i, 6), L.ancillas[i][2], 6, 11, L.alpha),
			cirq.CNOT(L.qubit(i, 4), L.ancillas[i][2]),
			chain_error(L.qubit(i, 4), L.ancillas[i][2], 4, 11, L.alpha),
			cirq.CNOT(L.qubit(i, 7), L.ancillas[i][2]),
			chain_error(L.qubit(i, 7), L.ancillas[i][2], 7, 11, L.alpha),
			cirq.measure(L.ancillas[i][2], key='ancilla2'),

			cirq.CNOT(L.qubit(i, 5), L.ancillas[i][3]),
			chain_error(L.qubit(i, 5), L.ancillas[i][3], 5, 12, L.alpha),
			cirq.CNOT(L.qubit(i, 8), L.ancillas[i][3]),
			chain_error(L.qubit(i, 8), L.ancillas[i][3], 8, 12, L.alpha),
			cirq.measure(L.ancillas[i][3], key='ancilla3'),


			# measure X stabs
			cirq.H(L.ancillas[i][4]),
			cirq.CNOT(L.ancillas[i][4], L.qubit(i, 1)),
			chain_error(L.ancillas[i][4], L.qubit(i, 1), 13, 1, L.alpha),
			cirq.CNOT(L.ancillas[i][4], L.qubit(i, 2)),
			chain_error(L.ancillas[i][4], L.qubit(i, 2), 13, 2, L.alpha),
			cirq.H(L.ancillas[i][4]),
			cirq.measure(L.ancillas[i][4], key='ancilla4'),

			cirq.H(L.ancillas[i][5]),
			cirq.CNOT(L.ancillas[i][5], L.qubit(i, 0)),
			chain_error(L.ancillas[i][5], L.qubit(i, 0), 14, 0, L.alpha),
			cirq.CNOT(L.ancillas[i][5], L.qubit(i, 1)),
			chain_error(L.ancillas[i][5], L.qubit(i, 1), 14, 1, L.alpha),
			cirq.CNOT(L.ancillas[i][5], L.qubit(i, 3)),
			chain_error(L.ancillas[i][5], L.qubit(i, 3), 14, 3, L.alpha),
			cirq.CNOT(L.ancillas[i][5], L.qubit(i, 4)),
			chain_error(L.ancillas[i][5], L.qubit(i, 4), 14, 4, L.alpha),
			cirq.H(L.ancillas[i][5]),
			cirq.measure(L.ancillas[i][5], key='ancilla5'),

			cirq.H(L.ancillas[i][6]),
			cirq.CNOT(L.ancillas[i][6], L.qubit(i, 4)),
			chain_error(L.ancillas[i][6], L.qubit(i, 4), 15, 4, L.alpha),
			cirq.CNOT(L.ancillas[i][6], L.qubit(i, 5)),
			chain_error(L.ancillas[i][6], L.qubit(i, 5), 15, 5, L.alpha),
			cirq.CNOT(L.ancillas[i][6], L.qubit(i, 7)),
			chain_error(L.ancillas[i][6], L.qubit(i, 7), 15, 7, L.alpha),
			cirq.CNOT(L.ancillas[i][6], L.qubit(i, 8)),
			chain_error(L.ancillas[i][6], L.qubit(i, 8), 15, 8, L.alpha),
			cirq.H(L.ancillas[i][6]),
			cirq.measure(L.ancillas[i][6], key='ancilla6'),

			cirq.H(L.ancillas[i][7]),
			cirq.CNOT(L.ancillas[i][7], L.qubit(i, 6)),
			chain_error(L.ancillas[i][7], L.qubit(i, 6), 16, 6, L.alpha),
			cirq.CNOT(L.ancillas[i][7], L.qubit(i, 7)),
			chain_error(L.ancillas[i][7], L.qubit(i, 7), 16, 7, L.alpha),
			cirq.H(L.ancillas[i][7]),
			cirq.measure(L.ancillas[i][7], key='ancilla7')
		)
	# circuit that simulates error from correcting process
	else:
		circuit = cirq.Circuit(
			initLogicalQubits(L),

			# measure Z stabs
			cirq.CNOT(L.qubit(i, 0), L.ancillas[i][0]),
			cirq.CNOT(L.qubit(i, 3), L.ancillas[i][0]),
			cirq.measure(L.ancillas[i][0], key='ancilla0'),

			cirq.CNOT(L.qubit(i, 1), L.ancillas[i][1]),
			cirq.CNOT(L.qubit(i, 4), L.ancillas[i][1]),
			cirq.CNOT(L.qubit(i, 2), L.ancillas[i][1]),
			cirq.CNOT(L.qubit(i, 5), L.ancillas[i][1]),
			cirq.measure(L.ancillas[i][1], key='ancilla1'),

			cirq.CNOT(L.qubit(i, 3), L.ancillas[i][2]),
			cirq.CNOT(L.qubit(i, 6), L.ancillas[i][2]),
			cirq.CNOT(L.qubit(i, 4), L.ancillas[i][2]),
			cirq.CNOT(L.qubit(i, 7), L.ancillas[i][2]),
			cirq.measure(L.ancillas[i][2], key='ancilla2'),

			cirq.CNOT(L.qubit(i, 5), L.ancillas[i][3]),
			cirq.CNOT(L.qubit(i, 8), L.ancillas[i][3]),
			cirq.measure(L.ancillas[i][3], key='ancilla3'),


			# measure X stabs
			cirq.H(L.ancillas[i][4]),
			cirq.CNOT(L.ancillas[i][4], L.qubit(i, 1)),
			cirq.CNOT(L.ancillas[i][4], L.qubit(i, 2)),
			cirq.H(L.ancillas[i][4]),
			cirq.measure(L.ancillas[i][4], key='ancilla4'),

			cirq.H(L.ancillas[i][5]),
			cirq.CNOT(L.ancillas[i][5], L.qubit(i, 0)),
			cirq.CNOT(L.ancillas[i][5], L.qubit(i, 1)),
			cirq.CNOT(L.ancillas[i][5], L.qubit(i, 3)),
			cirq.CNOT(L.ancillas[i][5], L.qubit(i, 4)),
			cirq.H(L.ancillas[i][5]),
			cirq.measure(L.ancillas[i][5], key='ancilla5'),

			cirq.H(L.ancillas[i][6]),
			cirq.CNOT(L.ancillas[i][6], L.qubit(i, 4)),
			cirq.CNOT(L.ancillas[i][6], L.qubit(i, 5)),
			cirq.CNOT(L.ancillas[i][6], L.qubit(i, 7)),
			cirq.CNOT(L.ancillas[i][6], L.qubit(i, 8)),
			cirq.H(L.ancillas[i][6]),
			cirq.measure(L.ancillas[i][6], key='ancilla6'),

			cirq.H(L.ancillas[i][7]),
			cirq.CNOT(L.ancillas[i][7], L.qubit(i, 6)),
			cirq.CNOT(L.ancillas[i][7], L.qubit(i, 7)),
			cirq.H(L.ancillas[i][7]),
			cirq.measure(L.ancillas[i][7], key='ancilla7')
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

		getCorrectionGate(L.qubit(index, 0), corrections[0]),
		getCorrectionGate(L.qubit(index, 1), corrections[1]),
		getCorrectionGate(L.qubit(index, 2), corrections[2]),
		getCorrectionGate(L.qubit(index, 3), corrections[3]),
		getCorrectionGate(L.qubit(index, 4), corrections[4]),
		getCorrectionGate(L.qubit(index, 5), corrections[5]),
		getCorrectionGate(L.qubit(index, 6), corrections[6]),
		getCorrectionGate(L.qubit(index, 7), corrections[7]),
		getCorrectionGate(L.qubit(index, 8), corrections[8]),
		cirq.measure(L.qubit(index, 0), key='result0'),
		cirq.measure(L.qubit(index, 1), key='result1'),
		cirq.measure(L.qubit(index, 2), key='result2'),
		cirq.measure(L.qubit(index, 3), key='result3'),
		cirq.measure(L.qubit(index, 4), key='result4'),
		cirq.measure(L.qubit(index, 5), key='result5'),
		cirq.measure(L.qubit(index, 6), key='result6'),
		cirq.measure(L.qubit(index, 7), key='result7'),
		cirq.measure(L.qubit(index, 8), key='result8')
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
	print(str(np.random.uniform(0,1)))
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

	L = LogicalQubits(2, 0.0001, 0, True)
	L.gateOnLogical(cirq.X, 0)
	L.gateOnLogical(cirq.CNOT, 0, 1)
	print('Flip first then CNOT gate: 1st qubit state (error prone) = ' + str(measureLogicalQubit(L, 0)))
	print('2nd qubit state = ' + str(measureLogicalQubit(L, 1)))

	#L = LogicalQubits(2, 0.01, 0.01, True)
	#L.gateOnLogical(cirq.X, 0)
	#repetitions = 1000
	#for i in range(repetitions):
	#	L.gateOnLogical(cirq.CNOT, 0, 1)
	#print('1000 CNOTS result:')
	#print('1st qubit state = ' + str(measureLogicalQubit(L, 0)))
	#print('2nd qubit state = ' + str(measureLogicalQubit(L, 1)))

	#L = LogicalQubits(2)
	#L.gateOnLogical(cirq.X, 1)
	#L.gateOnLogical(cirq.CNOT, 0, 1)
	#print('Flip second then CNOT gate: 1st qubit state = ' + str(measureLogicalQubit(L, 0)))
	#print('2nd qubit state = ' + str(measureLogicalQubit(L, 1)))


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