from src.exchanges import Uniswap, SushiSwap
from arbbot import optimal_amount
import src.config as cf
from arbbot.dt_manager import get_atm_opps

from pprint import pprint


def main_sync(w3, atm_opps):
    responses = [check4prof(atm_opp) for atm_opp in atm_opps]
    return responses


def fetch_reserves(atm_opp):
    pool1, pool2 = atm_opp.pool1, atm_opp.pool2
    ex1 = exchanges[pool1.exchange]
    ex2 = exchanges[pool2.exchange]

    *reserve_pool1, _ = ex1.get_reserves(pool1.address)
    *reserve_pool2, _ = ex2.get_reserves(pool2.address)
    reserve_pool1_tkn1 = reserve_pool1[atm_opp.tkn1]/10**(pool1.tokens[atm_opp.tkn1].decimal)
    reserve_pool1_tkn2 = reserve_pool1[atm_opp.tkn2]/10**(pool1.tokens[atm_opp.tkn2].decimal)
    reserve_pool2_tkn1 = reserve_pool2[atm_opp.tkn1]/10**(pool2.tokens[atm_opp.tkn1].decimal) 
    reserve_pool2_tkn2 = reserve_pool2[atm_opp.tkn2]/10**(pool2.tokens[atm_opp.tkn2].decimal)

    return reserve_pool1_tkn1, reserve_pool1_tkn2, reserve_pool2_tkn1, reserve_pool2_tkn2


def check4prof(atm_opp):
    r_p1_t1, r_p1_t2, r_p2_t1, r_p2_t2 = fetch_reserves(atm_opp)
    params = {"reserveOfToken1InPool1": r_p1_t2, 
              "reserveOfToken2InPool1": r_p1_t1, 
              "reserveOfToken1InPool2": r_p2_t2, 
              "reserveOfToken2InPool2": r_p2_t1, 
              "feeInPool1": atm_opp.pool1.fee,
              "feeInPool2": atm_opp.pool2.fee
             }
    optimimal_amount = calculate_optimized(params)

    return atm_opp.symbol, optimimal_amount


def calculate_optimized(params):
    result1 = optimal_amount.run(params)
    result2 = optimal_amount.run(params, reverse=1)

    return result1, result2


def run1():
    global exchanges
    import time
    t0 = time.time()
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    exchanges = {"uniswap": Uniswap(w3), "sushiswap": SushiSwap(w3)}
    atm_opps = get_atm_opps(select=["amplweth_ssuni"])
    t1 = time.time()
    rs = main_sync(w3, atm_opps)
    t2 = time.time()
    for r in rs:
        pprint(r)
    t3 = time.time()

    print("printing: ", t3-t2)
    print("calculation: ", t2-t1)
    print("initialization: ", t1-t0)


def run2():
    params = {"reserveOfToken1InPool2": 20538.44112209466, 
              "reserveOfToken2InPool2": 14678357.322432265, 
              "reserveOfToken1InPool1": 2197.664604672419, 
              "reserveOfToken2InPool1": 1572474.829665538, 
              "feeInPool1": 0.003,
              "feeInPool2": 0.003
             }
    result1 = optimal_amount.run(params)
    pprint(result1)


def run3():
    global exchanges
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    exchanges = {"uniswap": Uniswap(w3), "sushiswap": SushiSwap(w3)}
    atm_opps = get_atm_opps(select=["amplweth_ssuni"])
    amplweth = atm_opps[0]
    result3 = fetch_reserves(amplweth)
    pprint(result3)


if __name__ == "__main__":  
    run2()