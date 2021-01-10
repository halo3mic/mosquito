import websockets
import asyncio
from pprint import pprint
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import web3

import src.config as cf
import src.exchanges as ex
from arbbot.dt_manager import deserialize
import asyncio


# def call_method(ws_path, from_address, to_address, data):


#     # {"jsonrpc":"2.0","method":"eth_call","params": [{"from": "0xb60e8dd61c5d32be8058bb8eb970870f07233155","to": "0xd46e8dd67c5d32be8058bb8eb970870f07244567","gas": "0x76c0","gasPrice": "0x9184e72a000","value": "0x9184e72a","data": "0xd46e8dd67c5d32be8d46e8dd67c5d32be8058bb8eb970870f072445675058bb8eb970870f072445675"}, "latest"],"id":1}
#     async def _start_listening():
#         async with websockets.connect(ws_path, ping_interval=None) as websocket:
#             await websocket.send(self.provider.ws_blocks_request)
#             await websocket.recv()
#             opp_event = None
#             while 1:
#                 header = await websocket.recv()
#                 recv_tm = time.time()
#                 if opp_event: 
#                     opp_event.kill()
#                 opp_event = Process(target=self.action, args=(header, recv_tm, storage, prices))
#                 gas_price_event = Process(target=self.gas_price_updater, args=(prices,))
#                 opp_event.start()
#                 gas_price_event.start()
#     while 1:
#         try:
#             asyncio.get_event_loop().run_until_complete(_start_listening())
#         except ConnectionClosed:
#             continue

async def uniswap_reserve(w3, pool_address):
    pool_contract = w3.eth.contract(address=pool_address, abi=cf.abi("uniswapv2_pool"))
    return pool_contract.functions.getReserves().call()


def fetch_reserves(pool):
    exchange_contract = exchanges[pool.exchange]
    *reserve_per_tkn, _ = exchange_contract.get_reserves(pool.address)
    reserve = dict((pool.tokens[i], reserve_per_tkn[i]) for i in range(len(reserve_per_tkn)))
    return pool.id, reserve

async def _fetch_pools(w3, pools):
    tasks = [await asyncio.create_task(uniswap_reserve(w3, p.address)) for p in pools]
    return await asyncio.gather(*tasks)


def start_pool_fetching(w3, pools):
    w3.eth.retrieve_caller_fn = web3.module.retrieve_async_method_call_fn(w3, w3.eth)
    return asyncio.get_event_loop().run_until_complete(_fetch_pools(w3, pools))

# def get_reserve_fun(pool):
#     pool_contract = w3.eth.contract(address=pool.address, abi=cf.abi("uniswapv2_pool"))
#     return pool_contract.functions.getReserves()


provider_name = "infura"
w3 = cf.web3_api_session(provider_name)
uniswap = ex.Uniswap(w3)
sushiswap = ex.SushiSwap(w3)
exchanges = {"sushiswap": sushiswap, "uniswap": uniswap}

instructions = deserialize()
all_pools = []
for pool in (p for i in instructions.values() for p in (i.pool1, i.pool2)):
    if pool not in all_pools:
        all_pools.append(pool)

# threads_init = [Thread(target=fetch_reserves, args=(p,)) for p in all_pools]

import web3
t0 = time.time()


# reserves = [fetch_reserves(pool) for pool in all_pools[:5]]
# with ThreadPoolExecutor(max_workers=len(all_pools)) as executor:
#     reserves = executor.map(fetch_reserves, all_pools)
# [t.start() for t in threads_init]
# reserves = [t.join() for t in threads_init]
# pool1 = all_pools[0]
# fetch_reserves(pool1)
start_pool_fetching(w3, all_pools)

t1 = time.time()
pprint(list(reserves))


print(f"Runtime: {t1-t0:.2f} sec")
# call_transaction = {""}
