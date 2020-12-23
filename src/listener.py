from multiprocessing import Process, Queue
from web3 import Web3
import websockets
import asyncio
import time
import json
import csv
import os

from src.helpers import send2archer, payload2bytes, save_logs
from src.opportunities import EmptySet
from arbbot.main import ArbBot
import src.config as cf


class OpportunityManager:

    def __init__(self, avl_opps, provider, save_logs, print_logs):
        self.provider = provider
        self.opps = self.get_opps(avl_opps)
        self.save_logs = save_logs
        self.print_logs = print_logs

    def get_opps(self, avl_opps):
        w3 = Web3(Web3.HTTPProvider(self.provider.html_path))
        return [plan(w3) for plan in avl_opps]

    def process_opps(self, block_number, timestamp, state, recv_tm):
        stdout_str = f"  BLOCK NUMBER: {block_number}  ".center(80, "#")   
        for opp in self.opps:
            opp.import_state(state.get(str(opp), {}))  # Load previus state of the opportunity
            t0 = time.time()
            opp_response = opp(block_number, timestamp)
            t1 = time.time()
            state[str(opp)] = opp.export_state()  # Save current state 
            processing_time_opp = t1 - t0
            processing_time_all = t1 - recv_tm

            stats = {"blockNumber": block_number, 
                     "blockTimestamp": timestamp, 
                     "receivingTime": int(recv_tm), 
                     "oppProcessingTime": processing_time_opp, 
                     "wholeProcessingTime": processing_time_all,
                     "opportunityFound": opp_response["status"], 
                     "providerName": self.provider.name, 
                     "opportunity": str(opp), 
                     "byteload": opp_response["byteload"], 
                     "profit": opp_response["profit"]
                     }
            if self.save_logs:
                save_logs(stats, cf.save_logs_path)

            stdout_str += f"\nOPP {opp}: {bool(opp_response)}"
            stdout_str += f"\nTime taken: {processing_time_all:.4f} sec"
            stdout_str += f"\nLatency: {recv_tm-timestamp:.2f} sec"
        if self.print_logs:
            stdout_str += "\n"+"_"*80
            os.system("clear")
            print(stdout_str)

        return state


class Listener:

    def __init__(self, provider_name, avl_opps, save_logs=True, print_logs=True):
        self.provider = cf.provider(provider_name)
        self.opportunity_manager = OpportunityManager(avl_opps, self.provider, save_logs, print_logs)

    def header_handler(self, header):
        msg = json.loads(header)["params"]["result"]
        block = int(msg["number"].lstrip("0x"), 16)
        timestamp = int(msg["timestamp"].lstrip("0x"), 16)
        return block, timestamp

    def action(self, raw_header, queue, recv_tm):
        block_number, timestamp = self.header_handler(raw_header)
        # last_state = queue.get()
        last_state = {}
        new_state = self.opportunity_manager.process_opps(block_number, timestamp, last_state, recv_tm)
        # queue.put(new_state)

    def run_block_listener(self):
        q = Queue()
        q.put({})
        async def _start_listening():
            async with websockets.connect(self.provider.ws_path, ping_interval=None) as websocket:
                await websocket.send(self.provider.ws_blocks_request)
                await websocket.recv()
                future_event = None
                while 1:
                    header = await websocket.recv()
                    recv_tm = time.time()
                    if future_event: 
                        future_event.kill()
                    future_event = Process(target=self.action, args=(header, q, recv_tm))
                    future_event.start()

        return asyncio.get_event_loop().run_until_complete(_start_listening())


if __name__=="__main__":
    avl_opps = [ArbBot]
    provider_name = "chainStackBlocklytics"
    listener = Listener(provider_name, avl_opps)
    # listener.run_time_listener()
    listener.run_block_listener()


    