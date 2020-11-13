from code1 import *
import matplotlib.pyplot as plt

def find_CNOT_error_rate(pdark, repetitions):
	successes = 0
	for i in range(repetitions):
		L = LogicalQubits(2, pdark, 0, True)
		L.gateOnLogical(cirq.X, 0)
		L.gateOnLogical(cirq.CNOT, 0, 1)
		L1 = measureLogicalQubit(L, 0)
		L2 = measureLogicalQubit(L, 1)
		if (L1 == 1) and (L2 == 1):
			successes += 1
	return (repetitions - successes) / repetitions


def graph_pdark_vary(num_trials, init_pdark, increment):
	pdark_vals = np.zeros(num_trials)
	error_vals = np.zeros(num_trials)

	pdark = init_pdark
	for i in range(num_trials):
		print('Trial ' + str(i) + ':')
		pdark_vals[i] = pdark
		error_vals[i] = find_CNOT_error_rate(pdark, 1000)
		print('alpha = ' + str(pdark_vals[i]))
		print('Error rate = ' + str(error_vals[i]))
		pdark += increment

	plt.title('Error rate vs. alpha')
	plt.plot(pdark_vals, error_vals)
	plt.ylabel('Error rate')
	plt.xlabel('alpha')

	plt.show()


def main():
	num_trials = 100
	init_alpha = 0.01
	init_pdark = 0.01
	increment = 0.01
	
	graph_pdark_vary(num_trials, init_pdark, increment)




if __name__ == '__main__':
    main()