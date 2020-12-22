from src.exchanges import Uniswap, SushiSwap
from arbbot import optimal_amount
import src.config as cf
from arbbot.dt_manager import get_atm_opps

from pprint import pprint


def main_sync(w3, atm_opps):
    responses = [check4prof(atm_opp) for atm_opp in atm_opps]
    return responses


def check4prof(atm_opp):
    pool1, pool2 = atm_opp.pool1, atm_opp.pool2
    exchanges = {"uniswap": Uniswap(w3), "sushiswap": SushiSwap(w3)}
    ex1 = exchanges[pool1.exchange]
    ex2 = exchanges[pool2.exchange]

    *reserve_pool1, _ = ex1.get_reserves(pool1.address)
    *reserve_pool2, _ = ex2.get_reserves(pool2.address)
    reserve_pool1_tkn1 = reserve_pool1[atm_opp.tkn1]/10**(pool1.tokens[atm_opp.tkn1].decimal)
    reserve_pool1_tkn2 = reserve_pool1[atm_opp.tkn2]/10**(pool1.tokens[atm_opp.tkn2].decimal)
    reserve_pool2_tkn1 = reserve_pool2[atm_opp.tkn1]/10**(pool2.tokens[atm_opp.tkn1].decimal) 
    reserve_pool2_tkn2 = reserve_pool2[atm_opp.tkn2]/10**(pool2.tokens[atm_opp.tkn2].decimal) 

    params = {"reserveOfToken1InPool1": reserve_pool1_tkn2, 
              "reserveOfToken2InPool1": reserve_pool1_tkn1, 
              "reserveOfToken1InPool2": reserve_pool2_tkn2, 
              "reserveOfToken2InPool2": reserve_pool2_tkn1, 
              "feeInPool1": pool1.fee,
              "feeInPool2": pool2.fee
             }
    result1 = optimal_amount.run(params)
    result2 = optimal_amount.run(params, reverse=1)
    return atm_opp.symbol, (result1, result2)


if __name__ == "__main__":
    import time
    t0 = time.time()
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    atm_opps = get_atm_opps(select=["wbtcweth_ssuni"])
    t1 = time.time()
    rs = main_sync(w3, atm_opps)
    t2 = time.time()
    for r in rs:
        pprint(r)
    t3 = time.time()

    print("printing: ", t3-t2)
    print("calculation: ", t2-t1)
    print("initialization: ", t1-t0)