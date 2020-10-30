from code1 import *



def pass_fail(cond):
    if cond:
        str = 'Passed'
    else:
        str = 'Failed'
    return str

# test to see if the final state is correct, if not, print states (maybe)
def test_logical_qubit(num_data_qubits):

	# try 1, 2, 3 qubit errors on 0 state logical qubit
	# try complex state logical qubit, make sure it is accurate
	# try 1, 2, 3 qubit errors on the complex state logical qubit

	# errors and qubit states are limited to Clifford gates until i modify code (initialize logical qubit with cirq circuit syntax rather than injecting gates)

	L = LogicalQubit(0)
	print('Initialize logical qubit to 0 state: ' + pass_fail(measureLogicalQubit(L) == 0) + '\n')
	print('Testing simple errors on a logical qubit in 0 state...' + '\n')

	#----------------------------------------
	#----------ONE FLIP ERROR TEST---------------------
	#-------------------------------------

	print('Checking single qubit errors...')

	err_count = 0
	check_one = True
	for i in range(num_data_qubits):
		injectError(cirq.X, L, i)
		if (measureLogicalQubit(L) != 0):
			check_one = False
			err_count += 1
			print('Error: From X gate on data qubit ' + str(i))

	for i in range(num_data_qubits):
		injectError(cirq.Y, L, i)
		if (measureLogicalQubit(L) != 0):
			check_one = False
			err_count += 1
			print('Error: From Y gate on data qubit ' + str(i))

	for i in range(num_data_qubits):
		injectError(cirq.Z, L, i)
		if (measureLogicalQubit(L) != 0):
			check_one = False
			err_count += 1
			print('Error: From Z gate on data qubit ' + str(i))

	if (err_count != 0):
		print('Number of errors: ' + str(err_count))
	print('Single qubit error test: ' + pass_fail(check_one) + '\n')

	#----------------------------------------
	#----------TWO ERROR TEST---------------------
	#-------------------------------------

	print('Checking two qubit errors...')

	err_count = 0
	check_two = True
	for i in range(3 * num_data_qubits):
		if (i < num_data_qubits):
			first_gate = cirq.X
		elif (i < 2 * num_data_qubits):
			first_gate = cirq.Y
		else:
			first_gate = cirq.Z 

		k = i % num_data_qubits

		for j in range(k, num_data_qubits):
			injectError(first_gate, L, k)
			injectError(cirq.X, L, j)
			if (measureLogicalQubit(L) != 0):
				check_two = False
				err_count += 1
			#	print('Error: From '+str(first_gate)+' on ' + str(k) + ', X on ' + str(j))

		for j in range(k, num_data_qubits):
			injectError(first_gate, L, k)
			injectError(cirq.Y, L, j)
			if (measureLogicalQubit(L) != 0):
				check_two = False
				err_count += 1
			#	print('Error: From '+str(first_gate)+' on ' + str(k) + ', Y on ' + str(j))

		for j in range(k, num_data_qubits):
			injectError(first_gate, L, k)
			injectError(cirq.Z, L, j)
			if (measureLogicalQubit(L) != 0):
				check_two = False
				err_count += 1
			#	print('Error: From '+str(first_gate)+' on ' + str(k) + ', Z on ' + str(j))

	if (err_count != 0):
		print('Number of errors: ' + str(err_count))
	print('Two qubit error test: ' + pass_fail(check_two) + '\n')

	#----------------------------------------
	#----------THREE ERROR TEST---------------------
	#-------------------------------------

	print('Checking three qubit errors...')

	err_count = 0
	check_three = True
	for n in range(3 * num_data_qubits):
		if (n < num_data_qubits):
			first_gate = cirq.X
		elif (n < 2 * num_data_qubits):
			first_gate = cirq.Y
		else:
			first_gate = cirq.Z 

		i = n % num_data_qubits

		for m in range(i, num_data_qubits):
			if (m < num_data_qubits):
				second_gate = cirq.X
			elif (m < 2 * num_data_qubits):
				second_gate = cirq.Y
			else:
				second_gate = cirq.Z 

			j = m % num_data_qubits

			for k in range(j, num_data_qubits):
				injectError(first_gate, L, i)
				injectError(second_gate, L, j)
				injectError(cirq.X, L, k)
				if (measureLogicalQubit(L) != 0):
					check_three = False
					err_count += 1
			#		print('Error: From '+str(first_gate)+' on ' + str(k) + ', '+str(second_gate)+' on ' + str(j) + ', X on ' + str(k))

			for k in range(j, num_data_qubits):
				injectError(first_gate, L, i)
				injectError(second_gate, L, j)
				injectError(cirq.Y, L, k)
				if (measureLogicalQubit(L) != 0):
					check_three = False
					err_count += 1
			#		print('Error: From '+str(first_gate)+' on ' + str(k) + ', '+str(second_gate)+' on ' + str(j) + ', Y on ' + str(k))

			for k in range(j, num_data_qubits):
				injectError(first_gate, L, i)
				injectError(second_gate, L, j)
				injectError(cirq.Z, L, k)
				if (measureLogicalQubit(L) != 0):
					check_three = False
					err_count += 1
			#		print('Error: From '+str(first_gate)+' on ' + str(k) + ', '+str(second_gate)+' on ' + str(j) + ', Z on ' + str(k))

	if (err_count != 0):
		print('Number of errors: ' + str(err_count))
	print('Three qubit error test: ' + pass_fail(check_three) + '\n')
	print('----------------------------------')

	#----------------------------------------
	#----------(more) COMPLEX STATE TEST---------------------
	#-------------------------------------

	# set logical qubit to complex state, inject random errors, make sure that statistics match
	# circuit = cirq.Circuit(cirq.H(q), cirq.amplitude_damp(0.2)(q), cirq.measure(q))

	print('Testing errors on a logical qubit with Hadamard gate applied...' + '\n')

	repetitions = 100
	std = 5
	zero_count = 0
	check = False

	print('Checking Hadamard gate without errors...')
	for i in range(repetitions):
		gateOnLogical(cirq.H, L)
		if (measureLogicalQubit(L) == 0):
			zero_count += 1

	print('Number of zeros measured: ' + str(zero_count))
	if (zero_count in range(int(repetitions/2 - 2*std), int(repetitions/2 + 2*std+1))):
		check = True
	print('Base test: ' + pass_fail(check) + '\n')

	#---------One qubit error injected---------------
	print('Checking performance for each single qubit error...')
	err_count = 0

	for n in range(3*num_data_qubits):
		zero_count = 0
		if (n < num_data_qubits):
			first_gate = cirq.X
		elif (n < 2 * num_data_qubits):
			first_gate = cirq.Y
		else:
			first_gate = cirq.Z
		i = n % num_data_qubits

		for j in range(repetitions):
			gateOnLogical(cirq.H, L)
			injectError(first_gate, L, i)
			if (measureLogicalQubit(L) == 0):
				zero_count += 1

		if (zero_count not in range(int(repetitions/2 - 2*std), int(repetitions/2 + 2*std+1))):
			err_count += 1
			print('Possible error ('+str(first_gate)+' on qubit '+str(i)+'): ' + str(zero_count) + ' zeros recorded')

	print('Number of errors: '+str(err_count))
	check_one = True
	if (err_count > 27*0.05):
		check_one = False

	print('One qubit error test: ' + pass_fail(check_one) + '\n')

	#--------------Two qubit errors injected-----------------
	print('Checking performance for all two qubit errors...')
	err_count = 0

	for n in range(3*num_data_qubits):
		if (n < num_data_qubits):
			first_gate = cirq.X
		elif (n < 2 * num_data_qubits):
			first_gate = cirq.Y
		else:
			first_gate = cirq.Z
		i = n % num_data_qubits

		for m in range(3*num_data_qubits):
			zero_count = 0
			if (m < num_data_qubits):
				second_gate = cirq.X
			elif (m < 2 * num_data_qubits):
				second_gate = cirq.Y
			else:
				second_gate = cirq.Z
			j = m % num_data_qubits

			for k in range(repetitions):
				gateOnLogical(cirq.H, L)
				injectError(first_gate, L, i)
				injectError(second_gate, L, j)
				if (measureLogicalQubit(L) == 0):
					zero_count += 1

			if (zero_count not in range(int(repetitions/2 - 2*std), int(repetitions/2 + 2*std+1))):
				err_count += 1
				print('Possible error ('+str(first_gate)+' on '+str(i)+', '+str(second_gate)+' on '+str(j)+'): ' + str(zero_count) + ' zeros recorded')

	print('Number of errors: '+str(err_count))
	check_two = True
	if (err_count > 729*0.05):
		check_two = False

	print('Two qubit error test: ' + pass_fail(check_two) + '\n')


def main():
	test_logical_qubit(9)

if __name__ == '__main__':
    main()