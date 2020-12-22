from arbbot.opp_checker import main_async
import src.config as cf

import csv
import websockets
from multiprocessing import Process, Queue
import asyncio
import time



def save_logs(row_content, save_as):
    # Move this function to helpers
    # + create listeners module
    with open(save_as, "a") as stats_file:
        writer = csv.DictWriter(stats_file, fieldnames=row_content.keys())
        # writer.writeheader()
        writer.writerow(row_content)


class ArbBot:

    save_logs_path = "./logs/arbbot.csv"

    def __init__(self, w3):
        self.web3 = w3
        self.last_timestamp = None

    def __call__(self):
        self.last_timestamp = time.time()
        responses = main_async(self.web3)
        for r in responses:
            print(r)
            name, results = r
            if results[0]["arb_available"]:
                profit = results[0]["estimated_output_amount"] - results[0]["optimal_input_amount"]
                self.save_opp(name, profit)
            if results[1]["arb_available"]:
                profit = results[1]["estimated_output_amount"] - results[1]["optimal_input_amount"]
                self.save_opp(name, profit)

    def save_opp(self, name, profit):
        data = {"name": name, "profit": profit, "timestamp": self.last_timestamp}
        save_logs(data, self.save_logs_path)


def run_block_listener(provider, fun):
    # time_zero = time.time()

    async def _start_listening():
        async with websockets.connect(provider.ws_path) as websocket:
            await websocket.send(provider.ws_blocks_request)
            await websocket.recv()
            future_event = None
            while 1:
                # print("Starting listening: ", time.time()-time_zero)   
                _ = await websocket.recv()
                # print("Finished listening: ", time.time()-time_zero)

                if future_event: 
                    future_event.kill()
                    # print("Killed process")
                future_event = Process(target=fun)
                future_event.start()

    return asyncio.get_event_loop().run_until_complete(_start_listening())


def run():
    provider_name = "chainStackBlocklytics"
    provider = cf.provider(provider_name)
    w3 = cf.web3_api_session(provider_name)
    bot = ArbBot(w3)
    run_block_listener(provider, bot)


if __name__ == "__main__":
    run()



