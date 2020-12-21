# The derivative is just a good approximation!!!


from pprint import pprint


def is_profitable(A1, B1, A2, B2, WA1, WB1, WA2, WB2, _, F2):
	"""Checks if derivative at 0 is positive. Positive derivative means profitable opportunity."""
	return (B1*A2*WA1*WB2)/((1-F2)*A1*B2*WB1*WA2) >= 1


def function_generator(A1, B1, A2, B2, WA1, WB1, WA2, WB2, F1, F2):
	"""
	Return functions for optimal amount calculation.

	A1: Reserves of token A in pool 1. 
	B1: Reserves of token B in pool 1.  
	A2: Reserves of token A in pool 2.   
	B2: Reserves of token B in pool 2.   
	WA1: Weight of token A in pool 1.
	WB1: Weight of token B in pool 1.  
	WA2: Weight of token A in pool 2.  
	WB2: Weight of token B in pool 2.  
	F1: Fee percentage of input amount for pool 1.
	F2: Fee percentage of input amount for pool 2.

	Function f(m): Part of the derivative of weighted-optimal-amount function.
	Function m(x): The input of function f(m).
	Function x(m): The inverse of function m(x).

	Note:
		The derivative of weighted-optimal-amount function was equated to 0 and shortned as much as possible. New variables were created to accomodate for that. 
		The "main" function for which the root is searched is f(m), where m is the result of function m(x). 
		Here first root of f(m) is found and inverse of m(x) is used to finally get the x.

		This method has two benefits and one shortcoming. 
			+ With more variables there is less calculation per each iteration when finding the root.
			+ Function m(x) has a property to squeeze the input (range of input is greater then range of output).This drops the number of required iterations significantly.
			- Because the m(x) squeezes the range it is also inaccurate in terms of f(x). Even with accuracy set to the 0 there will still be visible offset.  
	"""

	q1 = 1 - F1
	q2 = 1 - F2
	w1 = WA1/WB1
	w2 = WB2/WA2
	k1 = (A1**w1 * B1*A2*B2**w2 *WA1*WB2*q2) / (WB1*WA2) / (q2*B1*A1**w1)**(1/w1+1)
	k2 = q2*B1 + B2
	k3 = q2*A1**w1*B1

	def profit(amount_in):
		sub = B1*q2 + B2 - (q2*B1*A1**w1) / (q1*amount_in+A1)**w1
		p = A2*(1 - (B2/sub)**w2) - amount_in

		return p

	f = lambda m: (k2- m)**(1+w2) - m**(1+1/w1)*k1
	m = lambda x: k3 / (q1*x + A1)**w1
	x = lambda m: ((k3/m)**(1/w1)-A1)/q1

	return f, m, x, profit


def riddlers_method(fun, lower_bound, upper_bound, max_iter, accuracy):
	"""
	Root finding algorithm based on Riddler's method, more details here: https://en.wikipedia.org/wiki/Ridders%27_method.

		fun[function]: Function for which root shall be found. 
		x0[float]: Lower bound of the range where root can be found.
		x2[float]: Upper bound of the range where root can be found.
		max_iter[int]: Number of iterations allowed to find the root at specified accuracy.
		accuracy[float]: Accuracy of the desired result.

	Note: There can only be one root between lower and upper bound (lower and upper bound need to have opposings signs).
	"""

	def sign(num): 
		return (1, -1)[num<0]

	xl = lower_bound
	xh = upper_bound

	for i in range(max_iter):
		fl = fun(xl)
		fh = fun(xh)
		xm = (xl+xh)*0.5  # Middle value
		fm = fun(xm)

		newx = xm + (xm - xl)*sign(xl)*fm / (fm**2-fl*fh)**0.5
		fnew = fun(newx)

		# Finish if the result within accuracy
		if abs(fnew) < accuracy:
			print(f"{i} iterations")
			return newx
		else:
			candidate = xm if fm*fnew<0 else xl if fl*fnew<0 else xh
			xl = min(candidate, newx)
			xh = max(candidate, newx)
	else:
		raise Exception("Maximum iterations reached.")


def main(data):
	profitable = is_profitable(data["reserveOfToken1InPool1"], 
											    data["reserveOfToken2InPool1"], 
											    data["reserveOfToken1InPool2"], 
											    data["reserveOfToken2InPool2"], 
											    data["weightOfToken1Pool1"], 
											    data["weightOfToken2Pool1"], 
											    data["weightOfToken1Pool2"], 
											    data["weightOfToken2Pool2"], 
											    data["feeInPool1"], 
											    data["feeInPool2"]
											    )
	if profitable: 
		f, m, m_inv, profit = function_generator(data["reserveOfToken1InPool1"], 
												    data["reserveOfToken2InPool1"], 
												    data["reserveOfToken1InPool2"], 
												    data["reserveOfToken2InPool2"], 
												    data["weightOfToken1Pool1"], 
												    data["weightOfToken2Pool1"], 
												    data["weightOfToken1Pool2"], 
												    data["weightOfToken2Pool2"], 
												    data["feeInPool1"], 
												    data["feeInPool2"]
												    )
		# The minimum amount is 0 and the greatest is the reserve of the token we start in pool 1. Single root needs to be found in this range.
		# Since the root finding is done in terms of m(not x) the range also needs to be projected through function m
		a = m(0)
		b = m(data["reserveOfToken1InPool1"])
		result = riddlers_method(f, a, b, MAX_ITER, MAX_ITER)
		# Result is given in terms of m(not x) and needs to be converted to x
		optimal_amount = m_inv(result)
		profit = profit(optimal_amount)
		if profit > 0:
			return {"arb_available": True, "optimal_input_amount": optimal_amount, "estimated_output_amount": optimal_amount+profit}

	return {"arb_available": False}



if __name__=="__main__":
	MAX_ITER = 100
	ACCURACY = 10**-9

	data = 	{"reserveOfToken1InPool1": 270.56234, 
		     "reserveOfToken2InPool1": 6741, 
		     "reserveOfToken1InPool2": 363.66816, 
		     "reserveOfToken2InPool2": 8993, 
		     "weightOfToken1Pool1": 0.5, 
		     "weightOfToken2Pool1": 0.5, 
		     "weightOfToken1Pool2": 0.5, 
		     "weightOfToken2Pool2": 0.5, 
		     "feeInPool1": 0.003,
		     "feeInPool2": 0.003
		    }

	print(main(data))



	# Add safe guard
	# Test edge cases
	# Is the second root always negative? yes
	# What happens if there is no root there? if derivative at 0 is + then it must be


"IT DOES NOT WORK FOR SMALL AMOUNTS!!!"
For small amounts 