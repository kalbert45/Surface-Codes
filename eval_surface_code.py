from code1 import *
import matplotlib.pyplot as plt

def find_logical_success_rate(p, repetitions):
	successes = 0
	for i in range(repetitions):
		if (np.random.uniform(0,1) < 0.5):
			control = True
		else:
			control = False
		L = LogicalQubits(1, 0, True, p)
		if (control):
			L.gateOnLogical(cirq.X, 0)
		L1 = measureLogicalQubit(L, 0)
		if (control):
			if (L1 == 1):
				successes += 1
		else:
			if (L1 == 0):
				successes += 1
	return (successes) / repetitions


def eval_surface_code(num_trials, init_p, increment):
	p_vals = []
	control = []
	success_rate_vals = []

	p = init_p
	for i in range(num_trials):
		print('Trial ' + str(i) + ':')
		p_vals.append(p)
		control.append(1-p)
		success_rate_vals.append(find_logical_success_rate(p, 1000))
		print('Noise rate = ' + str(p_vals[i]))
		print('Logical Success rate = ' + str(success_rate_vals[i]))
		p += increment


	plt.title('Logical success rate vs. alpha')
	plt.plot(p_vals, success_rate_vals)
	#plt.plot(p_vals, control)
	#plt.legend(["Logical qubit success", "Regular qubit success"])
	plt.ylabel('success rate')
	plt.xlabel('alpha')

	plt.show()


def main():
	num_trials = 100
	init_p = 0.0001
	increment = 0.0001
	
	eval_surface_code(num_trials, init_p, increment)

if __name__ == '__main__':
    main()