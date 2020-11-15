from multiprocessing import Process, Queue
import websockets
import asyncio
import time
import json

from src.opportunities import HalfRekt, EmptySet
from src.config import *


def process(msg_org, queue, opps):
    msg = json.loads(msg_org)["params"]["result"]
    block_number = int(msg["number"].lstrip("0x"), 16)
    timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
    print(f"Latency: {time.time()-timestamp} | Block: {block_number}")
    STORAGE = queue.get()
    print(STORAGE)
    # check_plans(block_number)
    STORAGE["newthing"] = "this is a new entry"
    queue.put(STORAGE)


def check_plans(w3, block_number):
    # Go through opps
    pass
    # plans = [HalfRekt, EmptySet]
    # for plan in plans:
    #     print(f"Running: {repr(plan)}")
    #     hf = HalfRekt(w3, wallet_address)
    #     response = hf()
    #     # if payload: send_to_archer(payload)
    #     print(f"Finished with {plan}")

    #     return response
    # else:
    #     print("No opportunities!")


def execute(w3, payload, wallet_address):
    gas_price = w3.eth.gasPrice
    nonce = w3.eth.getTransactionCount(wallet_address)
    tx = {
          "gasLimit": payload["gasLimit"],
          "from": wallet_address,
          "to": payload["contractAddress"],
          "data": payload["calldata"]}

    tx_hash = w3.eth.sendTransaction(tx).hex()
    
    return tx_hash  


def ws_receiver(uri, data_request, process_fun):
    time_zero = time.time()
    q = Queue()
    q.put({})

    async def _start_listening():
        
        async with websockets.connect(uri) as websocket:
            await websocket.send(data_request)
            await websocket.recv()
            future_event = None
            while 1:
                # print("Starting listening: ", time.time()-time_zero)   
                message = await websocket.recv()
                # print("Finished listening: ", time.time()-time_zero)

                if future_event: 
                    future_event.kill()
                    # print("Killed process")
                future_event = Process(target=process_fun, args=(message, q))
                future_event.start()

    return asyncio.get_event_loop().run_until_complete(_start_listening())


if __name__=="__main__":
    provider_name = "infura"
    html_provider = NODE_INFO[provider_name]["html_path"]
    ws_provider = NODE_INFO[provider_name]["ws_path"]
    data_request = NODE_INFO[provider_name]["ws_blocks_request"]

    ws_receiver(ws_provider, data_request, process)

    