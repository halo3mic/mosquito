from multiprocessing import Process
from dotenv import dotenv_values
from pprint import pprint
from web3 import Web3

import asyncio
import websockets
import json
import time


t0 = time.time()


def uniswap(pool_address, input_amount, inverse=False):
    FEE = 0.003
    uni_pool = w3.eth.contract(address=pool_address, abi=ABIS["uniswapv2"])
    bal0, bal1, _ = uni_pool.functions.getReserves().call()
    if inverse: bal0, bal1 = bal1, bal0
    bal0 /= 10**18  # This can depend on the token
    bal1 /= 10**18  # This can depend on the token
    amount_out = (1 - bal1/(bal1+input_amount)) * bal0 * (1-FEE)
    
    return amount_out


def half_rekt(current_block_number):
    EXPLOITER = "0x223034EDbe95823c1160C16F26E3000315171cA9"
    HALFREKT = "0x404A03728Afd06fB934e4b6f0EaF67796912733A"
    UNISWAP_ETHNME = "0xddbE1dFC668233bb882014838DAE50deF5Ea967c"
    GAS_AMOUNT_REKT = 150000  # First time is a lot more

    # Get block info
    target = STORAGE.get("halfRekt_nextExploitBlockNumber")
    print("Stored target: ", target)
    # Make sure that it is available when the block comes - check each new block when diff becomes less than 10
    if not target or (target-current_block_number-1) < 10:
        half_rekt = w3.eth.contract(address=HALFREKT, abi=contract_abi)
        target = half_rekt.functions.nextExploitBlock().call()+1  # The executing block needs to be greater than nextExploitBlock
        print("Computed target: ", target)
        STORAGE["halfRekt_nextExploitBlockNumber"] = target
    # If the next block is the target
    if target <= current_block_number+1:
        print("Execute")
        half_rekt = w3.eth.contract(address=HALFREKT, abi=ABIS[HALFREKT])
        exp_bal = half_rekt.functions.balanceOf(EXPLOITER)
        reward_nme = exp_bal * 0.001
        reward_eth = uniswap(UNISWAP_ETHNME, reward_nme, inverse=1)

        # Create payload


# NEED TO APPROVE BEFORE SWAP!!!

def half_rekt_payout():
    EXPLOITER = "0x223034EDbe95823c1160C16F26E3000315171cA9"
    HALFREKT = "0x404A03728Afd06fB934e4b6f0EaF67796912733A"
    UNISWAP_ETHNME = "0xddbE1dFC668233bb882014838DAE50deF5Ea967c"
    half_rekt = w3.eth.contract(address=HALFREKT, abi=ABIS[HALFREKT])
    exp_bal = half_rekt.functions.balanceOf(EXPLOITER).call()
    reward_nme = exp_bal * 0.001 * 10**-18
    reward_eth = uniswap(UNISWAP_ETHNME, reward_nme, inverse=1)

    return reward_eth


def half_rekt_execute(amount_in, amount_out, tkn_slippage=0.01, time_slippage=120):
    UNISWAP_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    WETH9 = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    HALFREKT = "0x404A03728Afd06fB934e4b6f0EaF67796912733A"
    GAS_AMOUNT_TRADE = 200000
    halfrekt_payload = {"contractAddress": HALFREKT, 
                    "function": exploitTheExploiter, 
                    "args": [], 
                    "gasLimit": GAS_AMOUNT
                    }
    trade_payload = {"contractAddress": HALFREKT, 
                     "function": "swapExactTokensForTokens", 
                     "args": [amount_in, amount_out*(1-slippage), [HALFREKT, WETH9], env_vals['ADDRESS'], deadline], 
                     "gasLimit": GAS_AMOUNT_TRADE
                     }

    return halfrekt_payload, trade_payload


def process(current_block_number):
    plans = [half_rekt]
    for plan in plans:
        print(f"Running: {repr(plan)}")
        payload = plan(current_block_number)
        if payload: send_to_archer(payload)


def receiver():
    async def _start_listening():
        uri = node_path
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(data_request))
            await websocket.recv()
            future_event = None
            while 1:
                print("Starting listening: ", time.time()-t0)        
                message = await websocket.recv()
                msg = json.loads(message)["params"]["result"]
                block_number = int(msg["number"].lstrip("0x"), 16)
                timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
                print(f"Latency: {time.time()-timestamp} | Block: {block_number}")
                print("Finished listening: ", time.time()-t0)
                if future_event: future_event.kill(); print("Killed process")
                future_event = Process(target=process, args=(block_number,))
                future_event.start()
    return asyncio.get_event_loop().run_until_complete(_start_listening())






if __name__=="__main__":
    ABIS = {}
    STORAGE = {}
    env_vals = dotenv_values("../.env")  # INFURA_TOKEN & PRIVATE_KEY & ADDRESS
    
    HALFREKT_ABI_PATH = "../abis/0x404A03728Afd06fB934e4b6f0EaF67796912733A.json"
    UNISWAPV2_ABI_PATH = "../abis/uniswapv2.json"
    ABIS["0x404A03728Afd06fB934e4b6f0EaF67796912733A"] = json.dumps(json.load(open(HALFREKT_ABI_PATH)))
    ABIS["uniswapv2"] = json.dumps(json.load(open(UNISWAPV2_ABI_PATH)))
    node_path = f"https://mainnet.infura.io/v3/{env_vals['INFURA_TOKEN']}"
    w3 = Web3(Web3.HTTPProvider(node_path))
    
    data_request = {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}
    # receiver()
    current_block_number = w3.eth.blockNumber
    # process(current_block_number)


    # amount_out = uniswap("0xddbE1dFC668233bb882014838DAE50deF5Ea967c", 4000, inverse=1)
    # print(amount_out)
    
    # print(half_rekt_payout())
    from ..src.config import VAR1

    print(VAR1) 

