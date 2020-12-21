import time
from concurrent.futures import ThreadPoolExecutor

from src.exchanges import Uniswap, SushiSwap
from arbbot import optimal_amount
import src.config as cf

from pprint import pprint


def timeit(fun):
    def _wrapper():
        t0 = time.time()
        response = fun()
        tdiff = time.time()-t0
        print(f"Runtime: {tdiff:.2f}s")
        return response
    return _wrapper


def check4prof(ex1, ex2, pool1, pool2, fee1=0.003, fee2=0.003):
    ss_reserve_tkn1, ss_reserve_tkn2, _ =  ex1.get_reserves(pool1)
    uni_reserve_tkn1, uni_reserve_tkn2, _ = ex2.get_reserves(pool2)

    params = {"reserveOfToken1InPool1": uni_reserve_tkn2, 
            "reserveOfToken2InPool1": uni_reserve_tkn1, 
            "reserveOfToken1InPool2": ss_reserve_tkn2, 
            "reserveOfToken2InPool2": ss_reserve_tkn1, 
            "feeInPool1": 0.003,
            "feeInPool2": 0.003
            }
    result1 = optimal_amount.run(params)
    result2 = optimal_amount.run(params, reverse=1)
    return result1, result2


def async_check4prof(ex1, ex2):
    def _wrapper(pair):
        pool1 = cf.address(pair[0])
        pool2 = cf.address(pair[1])
        return check4prof(ex1, ex2, pool1, pool2)
    return _wrapper


@timeit
def main_sync():
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    ss = SushiSwap(w3)
    uni = Uniswap(w3)
    pools = [("ss_wbtcweth", "uni_wbtcweth"), 
             ("ss_linkweth", "uni_linkweth")]
    responses = []
    for pool_pair in pools:
        pool1 = cf.address(pool_pair[0])
        pool2 = cf.address(pool_pair[1])
        response = check4prof(ss, uni, pool1, pool2)
        responses.append(response)
    return responses


@timeit
def main_async():
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    ss = SushiSwap(w3)
    uni = Uniswap(w3)
    pools = [("ss_wbtcweth", "uni_wbtcweth"), 
             ("ss_linkweth", "uni_linkweth"),
             ("ss_daiweth", "uni_daiweth"),
             ("ss_sushiweth", "uni_sushiweth"),
             ("ss_yfiweth", "uni_yfiweth"),
             ("ss_kp3rweth", "uni_kp3rweth"),
             ("ss_snxweth", "uni_snxweth"),
             ]
    fun = async_check4prof(ss, uni)
    with ThreadPoolExecutor() as executor:
        responses = executor.map(fun, pools)

    return responses


if __name__ == "__main__":
    rs = main_async()
    for r in rs:
        pprint(r)
    
# print(f"SushiSwap reserves: \n\twBTC: {ss_reserve_wbtc}\n\twETH: {ss_reserve_weth}")
# print(f"Uniswap reserves: \n\twBTC: {uni_reserve_wbtc}\n\twETH: {uni_reserve_weth}")
# pprint(result)


