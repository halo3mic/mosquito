import time
import requests
from pprint import pprint

from src.config import *
from src.dev_main import execute, ws_receiver
from src.ganache import Ganache
from src.opportunities import HalfRekt, EmptySet
from src.helpers import *


target_block = 11213401
wallet_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
provider_path = NODE_INFO["alchemy"]["html_path"]
whitelisted=[wallet_address]

start_block_number = target_block-3
ganache_session = Ganache(provider_path, block_number=start_block_number, unlock=whitelisted, mine_interval=15)
ganache_session.start_node()
atexit.register(lambda: ganache_session.kill())  # Closes the node after python session is finished

w3 = Web3(Web3.HTTPProvider(ganache_session.node_path))
# low_timestamp = w3.eth.getBlock(target_block-3).timestamp
# high_timestamp = w3.eth.getBlock(target_block-1).timestamp
# print(high_timestamp-low_timestamp)
ganache_session.increase_timestamp(100)
ganache_session.mine()

block_timestamp = w3.eth.getBlock("latest").timestamp
block_number = w3.eth.blockNumber
balance_eth_start = w3.eth.getBalance(wallet_address)/10**18
print("ETH Balance at start: ", balance_eth_start)
print("Block number: ", block_number)
print("Timstamp: ", block_timestamp)

payload_approval = approve_erc20(ADDRESSES["tokens"]["esd"], ADDRESSES["uniswap"]["uniswapv2_router02"])
t0 = time.time()
es = EmptySet(w3, wallet_address)
payload = es(block_number, block_timestamp)
print(payload)
print(f"Payloads ready, time taken: {time.time()-t0} sec")

try:
    approval_hash = execute(w3, payload_approval, wallet_address)
    advance_hash = execute(w3, payload[0], wallet_address)

    approval_tx = w3.eth.waitForTransactionReceipt(approval_hash)
    advance_tx = w3.eth.waitForTransactionReceipt(advance_hash)
    trade_hash = execute(w3, payload[1], wallet_address)
    trade_tx = w3.eth.waitForTransactionReceipt(trade_hash)
except Exception as e:
    print(repr(e))
else:
    pprint(approval_tx)
    pprint(advance_tx)
    pprint(trade_tx)
    print("ESD Balance at end: ", balance_erc20(w3, wallet_address, ADDRESSES["tokens"]["esd"]))
    print("ETH Balance at end: ", w3.eth.getBalance(wallet_address)/10**18)
    print("Block number: ", w3.eth.getBlock("latest").number)
    print("Timestamp: ", w3.eth.getBlock("latest").timestamp)
    print(approval_tx.blockNumber)
    print(trade_tx.blockNumber)
    print(advance_tx.blockNumber)

