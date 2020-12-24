from dotenv import dotenv_values
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
    primes(1)
    print("Ended primes: ", time.time()-t0)

def controller():
    # Get the data
    with concurrent.futures.ProcessPoolExecutor() as executor:


        future1 = executor.submit(start_listening)
        print(future1.result())
        executor.close()
        future2 = executor.submit(process, message)


def initialize_websocket(uri, request):
    websocket = websocket.connect(uri)
    await websocket.send(json.dumps(request)) 
    
    return websocket



def start_listening():
    async def _start_listening():
        uri = node_path
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(data_request))        
            while 1:
                message = await websocket.recv()
                await asyncio.sleep(3)
                return message
                

    return asyncio.get_event_loop().run_until_complete(_start_listening())


    # lets make two functions - one to send the initial request and the other to continue listening





if __name__=="__main__":
    env_vals = dotenv_values()  # INFURA_TOKEN & PRIVATE_KEY & ADDRESS
    node_path = f"wss://mainnet.infura.io/ws/v3/{env_vals['INFURA_TOKEN']}"
    w3 = Web3.WebsocketProvider(node_path)
    # print(w3.isConnected())
    request_data = {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}
    logs_request_data = {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["logs", {"address": "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"}]}
    pending_tx_request_data = {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}
    data_request = request_data
    # start_server = websockets.serve(hello, "localhost", 8765)


    
    # asyncio.run(start_listening())
    # print(result)
        # while 1:
        # print(w3.make_request(method="eth_subscribe", params=["logs", {"address": "0x8320fe7702b96808f7bbc0d4a888ed1468216cfd", "topics": ["0xd78a0cb8bb633d06981248b816e7bd33c2a35a6089241d099fa519e361cab902"]}]))
        # time.sleep(10)

    print(start_listening())
