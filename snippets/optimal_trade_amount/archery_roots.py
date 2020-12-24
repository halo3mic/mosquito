"""
This is python code for calculation of optimal buy amount for 2 step arbitrage on pools that have ratio between assets 50:50(Like on Uniswap).

Details:
	- Calculations
		- The calulation is based on the formula from www.desmos.com/calculator/nk9tzxezmn --> f(x)
		- The above formula was derived and steps can be seen here https://gitlab.com/blocklytics/archery/-/issues/174 --> f'(x)
	- Variables
		- A1 = Token1 reserves in pool 1
		- A2 = Token1 reserves in pool 2
		- B1 = Token2 reserves in pool 1
		- B2 = Token2 reserves in pool 2
		- F = Fees on the platform
	 - Meanings
	 	- Token1 = Asset to start and end the trade with 
	 	- Token2 = Intermediate asset 
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


if __name__ == "__main__":
	A1 = 2500000
	A2 = 2644755
	B1 = 9500
	B2 = 9385
	F = 0.003

	def reverse_pools():
		global A1, A2, B1, B2
		c = A1
		A1 = A2
		A2 = c
		print(A1)
		print(A2)
		c = B1
		B1 = B2
		B2 = c
		print(B1)
		print(B2)

	def reverse_tokens():
		global A1, A2, B1, B2
		c = A1
		A1 = B1
		B1 = c
		c = A2
		A2 = B2
		B2 = c
		print(A1)
		print(A2)
		print(B1)
		print(B2)

	
	# reverse_pools()
	# reverse_tokens()
	price1 = B1/A1
	price2 = B2/A2
	print(price1, price2)

	optimal_amount = get_optimal_trade_amount(A1, A2, B1, B2, F)
	print(optimal_amount)
	profit = get_profit(optimal_amount, A1, A2, B1, B2, F)
	print(profit)


