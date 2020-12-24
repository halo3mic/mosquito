from dotenv import dotenv_values
from pebble import ProcessPool
from pprint import pprint
from web3 import Web3
import concurrent.futures
import asyncio
import websockets
import json
import time


t0 = time.time()

def primes(n):
    return [i for i in range(2, n) if not any(i//a==i/a for a in range(2, i))]

def process(msg):
    print("Starting primes: ", time.time()-t0)
    primes(45000)
    print("Ended primes: ", time.time()-t0)


def controller():
    # Get the data
    data = receiver()
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    n = 0
    while 1:
        with ProcessPool(max_workers=8, max_tasks=1) as pool:
            n += 1
            print(f"This is loop {n}")
            future_reciver = pool.schedule(receiver)
            future_event = pool.schedule(process, args=[data])
            data = future_reciver.result()
            print(data[:10])
            pool.stop()


def receiver():
    async def _start_listening():
        uri = node_path
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(data_request))
            await websocket.recv()
            while 1:
                message = await websocket.recv()
                # msg = json.loads(message)["params"]["result"]
                # block_number = int(msg["number"].lstrip("0x"), 16)
                # timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
                # print(f"Latency: {time.time()-timestamp} | Block: {block_number} | Blocktimestamp at: {time.strftime('%H:%M:%S', time.localtime(timestamp))} | Found at :{time.strftime('%H:%M:%S', time.localtime(time.time()))}")
                print("_")
            # with ProcessPool(max_workers=8, max_tasks=1) as pool:
            #     future_event = None
            #     while 1:
            #         print("Starting listening: ", time.time()-t0)        
            #         message = await websocket.recv()
            #         msg = json.loads(message)["params"]["result"]
            #         block_number = int(msg["number"].lstrip("0x"), 16)
            #         timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
            #         print(f"Latency: {time.time()-timestamp} | Block: {block_number}")
            #         print("Finished listening: ", time.time()-t0)
            #         if future_event: future_event.cancel()
            #         future_event = pool.schedule(process, args=[message])
    return asyncio.get_event_loop().run_until_complete(_start_listening())






if __name__=="__main__":
    env_vals = dotenv_values()  # INFURA_TOKEN & PRIVATE_KEY & ADDRESS
    INFURA_URL = f"https://mainnet.infura.io/v3/{env_vals['INFURA_TOKEN']}"
    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    # node_path = f"wss://mainnet.infura.io/ws/v3/{env_vals['INFURA_TOKEN']}"
    # w3 = Web3.WebsocketProvider(node_path)
    # print(w3.isConnected())
    # request_data = {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}
    # logs_request_data = {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["logs", {"address": "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"}]}
    # pending_tx_request_data = {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}
    # data_request = request_data
    # # start_server = websockets.serve(hello, "localhost", 8765)
    # receiver()
    timeout = 1
    last_block = None
    while 1:
        time.sleep(timeout)
        latest_block = w3.eth.getBlock('latest')
        if last_block == latest_block:
            print("Old block")
            continue
        block_timestamp = latest_block['timestamp']
        print(f"Latency: {time.time()-block_timestamp} | Block number: {latest_block['number']}")
        last_block = latest_block