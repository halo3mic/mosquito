from multiprocessing import Process, Queue
import websockets
import asyncio
import time
import json
import os
import csv

from src.config import *
from src.opportunities import EmptySet


def process_w_log(msg_org, queue):
    receiving_time = time.time()
    msg = json.loads(msg_org)["params"]["result"]
    block_number = int(msg["number"].lstrip("0x"), 16)
    timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
    storage = queue.get()   
    
    os.system("clear")
    print(f"  BLOCK NUMBER: {block_number}  ".center(80, "#"))

    for opp in opps:
        opp.import_state(storage.get(str(opp), {}))
        t0 = time.time()
        opp_response = check_plans(opp, block_number, timestamp)
        t1 = time.time()
        storage[str(opp)] = opp.export_state()
        processing_time_opp = t1 - t0
        processing_time_all = t1 - receiving_time

        stats = {"blockNumber": block_number, 
                   "blockTimestamp": timestamp, 
                   "receivingTime": int(receiving_time), 
                   "oppProcessingTime": processing_time_opp, 
                   "wholeProcessingTime": processing_time_all,
                   "opportunityFound": bool(opp_response), 
                   "providerName": provider, 
                   "opportunity": str(opp), 
                   "byteload": opp_response
                   }
        log_stats(stats)



        print(f"OPP {opp}: {bool(opp_response)}")
        print(f"Time taken: {processing_time_all:.4f} sec")
        print(f"Latency: {receiving_time-timestamp:.2f} sec")
    queue.put(storage)
    print("_"*80)


def check_plans(opp, block_number, block_timestamp):
    byteload = opp(block_number, block_timestamp)
    return byteload


def log_stats(row_content):
    with open(RESULT_LOG_PATH, "a") as stats_file:
        writer = csv.DictWriter(stats_file, fieldnames=row_content.keys())
        # writer.writeheader()
        writer.writerow(row_content)


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


def main(provider_name, avl_opps):
    global opps, provider
    # Settings
    html_provider = NODE_INFO[provider_name]["html_path"]
    ws_provider = NODE_INFO[provider_name]["ws_path"]
    data_request = NODE_INFO[provider_name]["ws_blocks_request"]
    w3 = Web3(Web3.HTTPProvider(html_provider))

    # Globals vars
    opps = [plan(w3) for plan in avl_opps]
    provider = provider_name

    ws_receiver(ws_provider, data_request, process_w_log)


if __name__=="__main__":
    provider_name = "quickNode"
    avl_opps = [EmptySet]
    main(provider_name, avl_opps)


    