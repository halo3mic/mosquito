import csv
import json
import time
import asyncio
import websockets
from src.config import provider
from multiprocessing import Process, Queue


def process(provider_name):
    def _process(msg, q):
        rec_time = time.time()
        last_block = q.get()
        msg = json.loads(msg)["params"]["result"]
        block_number = int(msg["number"].lstrip("0x"), 16)
        timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
        first = False
        if block_number>last_block:
            # print("*"*50)
            # print(block_number)
            # print(rec_time - timestamp)
            # print(provider_name)  
            # print("*"*50)
            first = True
            q.put(block_number)
        else:
            q.put(last_block)
        stats = {"blockNumber": block_number, 
                 "blockTimestamp": timestamp, 
                 "timestamp": rec_time, 
                 "provider": provider_name, 
                 "first": first}
    
        log_results(stats)
    
    return _process


def default(org_fun):
    default_request = provider("infura").ws_blocks_request
    def wrapper(provider, q):
        uri = provider.ws_path
        name = provider.name
        process_fun = process(name)
        return org_fun(uri, default_request, process_fun, q)

    return wrapper


@default
async def start_listening(uri, data_request, process_fun, queue):
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
            future_event = Process(target=process_fun, args=(message, queue))
            future_event.start()


def log_results(results):
    LOG_SAVE_PATH = "./logs/nodeProvidersThreadedWS_gapp.csv"
    with open(LOG_SAVE_PATH, "a") as result_log:
        writer = csv.DictWriter(result_log, fieldnames=results.keys())
        writer.writerow(results)


async def handler(providers):
    q = Queue()
    q.put(0)
    threads = [start_listening(p, q) for p in providers]
    await asyncio.wait(threads)

def main():
    provider_names = ["infura", "quickNode", "alchemy", "chainStack"]
    providers = [provider(p) for p in provider_names]
    asyncio.get_event_loop().run_until_complete(handler(providers))


if __name__=="__main__":
    main()