"""
This is python code for calculation of optimal buy amount for 2 step arbitrage on pools that have ratio between assets 50:50(Like on Uniswap).

Details:
	- Calculations
		- The calulation is based on the formula from www.desmos.com/calculator/nk9tzxezmn --> f(x)
		- The above formula was derived and steps can be seen here https://gitlab.com/blocklytics/archery/-/issues/174 --> f'(x)
	- Variables
		- A1 = TokenA reserves in pool 1
		- A2 = TokenA reserves in pool 2
		- B1 = TokenB reserves in pool 1
		- B2 = TokenB reserves in pool 2
		- F = Fees on the platform
	 - Meanings
	 	- TokenA = Asset to start and end the trade with 
	 	- TokenB = Intermediate asset 
	 	- f'(x) represents the profit made by executing the trade with x tokens (start and end tokens need to be the same)
	 	- x represents the amount of tokens trade is started with 
	 	- The bigger root of f'(x)=0 represents the optimal start amount - where profit is the greatest
"""



def get_optimal_trade_amount(a1, a2, b1, b2, f):
	q = 1 - f

	a = -b1**2*q**4 - 2*b1*b2*q**3 - b2**2*q**2
	b = -2*b1*b2*a1*q**2 - 2*b2**2*a1*q
	c = b1*b2*a2*a1*q**2-b2**2*a1**2
	D_root = (b**2 - 4*a*c)**0.5
	root1 = (-b-D_root) / (2*a)
	root2 = (-b+D_root) / (2*a)

	return max(root1, root2)


def get_profit(x, a1, a2, b1, b2, f):
	q = 1 - f
	profit = -(x**2 * (q**2 *b1 + q*b2) + x*(a1*b2 - a2*q**2 *b1)) / (x*(q**2 *b1 + q*b2) + a1*b2)

	return profit


def main(input_data):
	optimal_amount = get_optimal_trade_amount(input_data["tknAp1"], 
											  input_data["tknAp2"], 
											  input_data["tknBp1"], 
											  input_data["tknBp2"], 
											  input_data["fee"]
											  )

	if optimal_amount > 0:
		profit = get_profit(optimal_amount,
							input_data["tknAp1"], 
						    input_data["tknAp2"], 
						    input_data["tknBp1"], 
						    input_data["tknBp2"], 
						    input_data["fee"]
						    )
		return {"arb": True, "optimal_amount": optimal_amount, "profit": profit}
	else:
		return {"arb": False}


if __name__ == "__main__":
	data = {"tknAp1": 2500000, 
		    "tknBp1": 9500, 
		    "tknAp2": 2650000, 
		    "tknBp2": 9700, 
		    "fee": 0.003
		    }
	result = main(data)

	print(result)






