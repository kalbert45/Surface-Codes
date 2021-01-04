from code1 import *
import matplotlib.pyplot as plt

def find_CNOT_error_rate(pdark, repetitions):
	successes = 0
	for i in range(repetitions):
		if (np.random.uniform(0,1) < 0.5):
			control = True
		else:
			control = False
		L = LogicalQubits(2, pdark, 0, True)
		if (control):
			L.gateOnLogical(cirq.X, 0)
		L.gateOnLogical(cirq.CNOT, 0, 1)
		L1 = measureLogicalQubit(L, 0)
		L2 = measureLogicalQubit(L, 1)
		if (control):
			if (L1 == 1) and (L2 == 1):
				successes += 1
		else:
			if (L1 == 0) and (L2 == 0):
				successes += 1
	return (repetitions - successes) / repetitions


def graph_pdark_vary(num_trials, init_pdark, increment):
	pdark_vals = []
	error_vals = []

	pdark = init_pdark
	for i in range(num_trials):
		print('Trial ' + str(i) + ':')
		pdark_vals.append(pdark)
		error_vals.append(find_CNOT_error_rate(pdark, 10000))
		print('alpha = ' + str(pdark_vals[i]))
		print('Error rate = ' + str(error_vals[i]))
		pdark += increment

		if (error_vals[i] > 0.03):
			break

	plt.title('Error rate vs. alpha (1 trap)')
	plt.plot(pdark_vals, error_vals)
	plt.ylabel('Error rate')
	plt.xlabel('alpha')

	plt.show()


def main():
	num_trials = 100
	init_alpha = 0.01
	init_pdark = 1e-6
	increment = 1e-6
	
	graph_pdark_vary(num_trials, init_pdark, increment)




if __name__ == '__main__':
    main()