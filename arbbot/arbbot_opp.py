import time
from concurrent.futures import ThreadPoolExecutor

from src.exchanges import Uniswap, SushiSwap
from arbbot import optimal_amount
import src.config as cf


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


def main_async(w3, atm_opps):
    with ThreadPoolExecutor() as executor:
        responses = executor.map(check4prof, atm_opps)
    return responses


if __name__ == "__main__":
    from arbbot.dt_manager import get_atm_opps
    from pprint import pprint
    import time

    t0 = time.time()
    provider_name = "quickNode"
    w3 = cf.web3_api_session(provider_name)
    atm_opps = get_atm_opps()
    rs = main_async(w3, atm_opps)
    for r in rs:
        pprint(r)

    print(f"Runtime: {time.time()-t0:.2f}s")



