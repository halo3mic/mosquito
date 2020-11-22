from multiprocessing import Process, Queue
from web3 import Web3
import websockets
import asyncio
import time
import json
import csv
import os

import src.config as cf
from src.opportunities import EmptySet


class Listener:

    save_logs_path = "./logs/stats.csv"

    def __init__(self, provider_name, avl_opps):
        self.provider = cf.provider(provider_name)
        self.opps = self._get_opps(avl_opps)
        # Make queue an attribute

    def _get_opps(self, avl_opps):
        w3 = Web3(Web3.HTTPProvider(self.provider.html_path))
        return [plan(w3) for plan in avl_opps]

    def process_block_headers(self, msg_org, queue, log=True, print_logs=True):
        receiving_time = time.time()
        msg = json.loads(msg_org)["params"]["result"]
        block_number = int(msg["number"].lstrip("0x"), 16)
        timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
        storage = queue.get()
        stdout_str = f"  BLOCK NUMBER: {block_number}  ".center(80, "#")   

        for opp in self.opps:
            opp.import_state(storage.get(str(opp), {}))
            t0 = time.time()
            opp_response = opp(timestamp)
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
                       "providerName": self.provider.name, 
                       "opportunity": str(opp), 
                       "byteload": opp_response
                       }
            if log:
                self.save_logs(stats)

            stdout_str += f"\nOPP {opp}: {bool(opp_response)}"
            stdout_str += f"\nTime taken: {processing_time_all:.4f} sec"
            stdout_str += f"\nLatency: {receiving_time-timestamp:.2f} sec"
        queue.put(storage)
        if print_logs:
            stdout_str += "\n"+"_"*80
            os.system("clear")
            print(stdout_str)


    def save_logs(self, row_content):
        with open(self.save_logs_path, "a") as stats_file:
            writer = csv.DictWriter(stats_file, fieldnames=row_content.keys())
            # writer.writeheader()
            writer.writerow(row_content)

    def run_block_listener(self):
        # time_zero = time.time()
        q = Queue()
        q.put({})

        async def _start_listening():
            
            async with websockets.connect(self.provider.ws_path) as websocket:
                await websocket.send(self.provider.ws_blocks_request)
                await websocket.recv()
                future_event = None
                while 1:
                    # print("Starting listening: ", time.time()-time_zero)   
                    message = await websocket.recv()
                    # print("Finished listening: ", time.time()-time_zero)

                    if future_event: 
                        future_event.kill()
                        # print("Killed process")
                    future_event = Process(target=self.process_block_headers, args=(message, q))
                    future_event.start()

        return asyncio.get_event_loop().run_until_complete(_start_listening())


    def process2(self, timestamp, opp, log=True, print_logs=True):
        t0 = time.time()
        opp_response = opp(timestamp)
        t1 = time.time()
        processing_time_opp = t1 - t0

        stats = {"blockNumber": None, 
                "blockTimestamp": None, 
                "receivingTime": int(t0), 
                "oppProcessingTime": processing_time_opp, 
                "wholeProcessingTime": processing_time_opp,
                "opportunityFound": bool(opp_response), 
                "providerName": self.provider.name, 
                "opportunity": str(opp), 
                "byteload": opp_response
                    }
        if opp_response and log:
            self.save_logs(stats)
        if print_logs:
            os.system("clear")
            print(f"Timestamp: {timestamp:.0f} | Opp found: {bool(opp_response)}")
            print(f"Time left: {opp.target_timestamp()-timestamp:.0f} sec | Process time: {processing_time_opp} sec")

    def run_time_listener(self, wait_time=1):
        while 1:
            timestamp = time.time()
            for opp in self.opps:
                # Later make this concurrent
                self.process2(timestamp, opp)
            time.sleep(wait_time)


if __name__=="__main__":
    avl_opps = [EmptySet]
    provider_name = "chainStackAsia"
    listener = Listener(provider_name, avl_opps)
    # listener.run_time_listener()
    listener.run_block_listener()


    