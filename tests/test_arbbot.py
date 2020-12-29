from arbbot.dt_manager import get_instructions 
from arbbot.main import ArbBot
import src.config as cf

from pprint import pprint
import time


def test_fetch_reserves():
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    bot = ArbBot(w3)
    selection = ["weth2wbtc2weth_uniswap2Sushiswap", 
                 "weth2snx2weth_uniswap2Sushiswap", 
                 "weth2wbtc2weth_sushiswap2Uniswap"]
    # selection = None
    instructions = get_instructions(select=selection)
    bot.instr = instructions
    reserves = {}
    for pool in (p for i in instructions for p in (i.pool1, i.pool2)):
        if pool.id not in reserves:
            reserves[pool.id] = bot.fetch_reserves(pool)
    pprint(reserves)


def test_async_fetch_reserves():
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    bot = ArbBot(w3)
    selection = ["weth2wbtc2weth_uniswap2Sushiswap", 
                 "weth2snx2weth_uniswap2Sushiswap", 
                 "weth2wbtc2weth_sushiswap2Uniswap"]
    # selection = None
    instructions = get_instructions(select=selection)
    bot.instr = instructions
    reserves = bot.async_fetch_reserves()
    pprint(reserves)


def test_run():
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    bot = ArbBot(w3)
    selection = ["weth2band2weth_uniswap2Sushiswap", ]
    selection = None
    instructions = get_instructions(select=selection)
    bot.instr = instructions
    bot.gas_price = 42*10**9
    r = bot.run()
    pprint(r)

def test_call():
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    bot = ArbBot(w3)
    # selection = ["weth2wbtc2weth_uniswap2Sushiswap", 
    #              "weth2snx2weth_uniswap2Sushiswap", 
    #              "weth2wbtc2weth_sushiswap2Uniswap"]
    selection = None
    instructions = get_instructions(select=selection)
    bot.instr = instructions
    response = bot(1, 1)
    pprint(response)


def test_form_bytecode():
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    bot = ArbBot(w3)
    opp = {
            "instrId": "I0001", 
            "instrSymbol": "weth2wbtc2weth_uniswap2Sushiswap", 
            "optimalAmount": 3.5, 
            "grossProfit": 0.25, 
            "netProfit": 0.1, 
            "gasCost": 0.15, 
            "gasAmount": 260000
            }
    block_timestamp = 0
    bytecode = bot.form_bytecode(opp, block_timestamp)

    return bytecode


if __name__ == "__main__":
    t0 = time.time()
    # test_fetch_reserves()
    # test_run()
    # pprint(get_instructions())
    test_form_bytecode()
    print(f"Runtime: {time.time()-t0} sec")


