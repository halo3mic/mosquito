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



def get_optimal_trade_amount(a1, a2, b1, b2, f1, f2):
    q1 = 1 - f1
    q2 = 1 - f2

    a = b1**2*q1**2*q2**2 + 2*b1*b2*q1**2*q2 + b2**2*q1**2
    b = 2*b1*b2*a1*q1*q2 + 2*b2**2*a1*q1
    c = b2**2*a1**2 - b1*b2*a2*a1*q1*q2
    D_root = (b**2 - 4*a*c)**0.5
    root1 = (-b-D_root) / (2*a)
    root2 = (-b+D_root) / (2*a)

    return max(root1, root2)


def get_profit(x, a1, a2, b1, b2, f1, f2):
    q1 = 1 - f1
    q2 = 1 - f2
    profit = -(x**2 * (q1*q2 *b1 + q1*b2) + x*(a1*b2 - a2*q1*q2 *b1)) / (x*(q1*q2 *b1 + q1*b2) + a1*b2)

    return profit


def calculate(input_data):
    optimal_amount = get_optimal_trade_amount(input_data["reserveOfToken1InPool1"], 
                                              input_data["reserveOfToken1InPool2"], 
                                               input_data["reserveOfToken2InPool1"], 
                                               input_data["reserveOfToken2InPool2"], 
                                                input_data["feeInPool1"], 
                                              input_data["feeInPool2"]
                                              )

    if optimal_amount > 0:
        profit = get_profit(optimal_amount, 
                            input_data["reserveOfToken1InPool1"], 
                            input_data["reserveOfToken1InPool2"], 
                            input_data["reserveOfToken2InPool1"], 
                            input_data["reserveOfToken2InPool2"], 
                            input_data["feeInPool1"], 
                            input_data["feeInPool2"]
                            )
        return {"arb_available": True, "optimal_input_amount": optimal_amount, "estimated_output_amount": optimal_amount+profit}
    else:
        return {"arb_available": False}


def _reverse_pools(input_data):
    reversed_data = {}
    reversed_data["reserveOfToken1InPool1"] = input_data["reserveOfToken1InPool2"]
    reversed_data["reserveOfToken1InPool2"] = input_data["reserveOfToken1InPool1"]
    reversed_data["reserveOfToken2InPool1"] = input_data["reserveOfToken2InPool2"]
    reversed_data["reserveOfToken2InPool2"] = input_data["reserveOfToken2InPool1"]
    reversed_data["feeInPool1"] = input_data["feeInPool2"]
    reversed_data["feeInPool2"] = input_data["feeInPool1"]
    return reversed_data


def run(input_data, reverse=False):
    if reverse:
        input_data = _reverse_pools(input_data)
    return calculate(input_data)


if __name__ == "__main__":
    data = {"reserveOfToken1InPool1": 270.56234, 
             "reserveOfToken2InPool1": 6741, 
             "reserveOfToken1InPool2": 363.66816, 
             "reserveOfToken2InPool2": 8993, 
            "feeInPool1": 0.003,
            "feeInPool2": 0.001
            }
    result = main(data)

    print(result)






