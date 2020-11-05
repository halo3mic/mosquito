import time
import requests
from pprint import pprint

from src.config import *
from src.dev_main import execute, ws_receiver
from src.ganache import start_ganache
from src.opportunities import HalfRekt, EmptySet
from src.helpers import *


t0 = time.time()
target_block = 11195961
wallet_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
provider_path = NODE_INFO["alchemy"]["html_path"]
whitelisted=[wallet_address]
# w3 = start_historical_node(provider_path, target-1, whitelisted=[wallet_address])

start_block_number = target_block-3
ganache_process, provider_path, accounts, private_keys = start_ganache(provider_path, block_number=start_block_number, mine_interval=None, unlock=whitelisted)
atexit.register(lambda: ganache_process.kill())  # Closes the node after python finishes
w3 = Web3(Web3.HTTPProvider(provider_path))

block_timestamp = w3.eth.getBlock("latest").timestamp
block_number = w3.eth.blockNumber
balance_eth_start = w3.eth.getBalance(wallet_address)/10**18
print("ETH Balance at start: ", balance_eth_start)
print("Block number: ", block_number)
print("Timstamp: ", block_timestamp)


try:
    es = EmptySet(w3, wallet_address)
    if es is None: raise Exception("No opportunity!")
    payload = es(block_number, block_timestamp)
    payload_approval = approve_erc20(ADDRESSES["tokens"]["esd"], ADDRESSES["uniswap"]["uniswapv2_router02"])
    print(f"Payloads ready, time taken: {time.time()-t0} sec")

    requests.post(provider_path, json.dumps({"jsonrpc": "2.0","method": "evm_increaseTime", "params": [100]}))
    requests.post(provider_path, json.dumps({"jsonrpc": "2.0","method": "evm_mine", "params": []}))

    approval_hash = execute(w3, payload_approval, wallet_address)
    advance_hash = execute(w3, payload[0], wallet_address)
    trade_hash = execute(w3, payload[1], wallet_address)

    approval_tx = w3.eth.waitForTransactionReceipt(approval_hash)
    advance_tx = w3.eth.waitForTransactionReceipt(advance_hash)
    trade_tx = w3.eth.waitForTransactionReceipt(trade_hash)
except Exception as e:
    print(repr(e))
else:
    print("ESD Balance at end: ", balance_erc20(w3, wallet_address, ADDRESSES["tokens"]["esd"]))
    print("ETH Balance at end: ", w3.eth.getBalance(wallet_address)/10**18)
    print("Block number: ", w3.eth.getBlock("latest").number)
    print("Timestamp: ", w3.eth.getBlock("latest").timestamp)

