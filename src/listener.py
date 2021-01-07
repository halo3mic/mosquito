from multiprocessing import Process, Manager
from websockets import ConnectionClosed
from web3 import Web3
import websockets
import asyncio
import time
import json
import csv
import os

from src.helpers import send2archer, payload2bytes, save_logs
from src.gas_manager import fetch_gas_price
from src.opportunities import EmptySet
from arbbot.main import ArbBot
import src.config as cf


class OpportunityManager:

    def __init__(self, w3, avl_opps, save_logs=True, print_logs=True, to_archer=True):
        self.w3 = w3
        self.opps = self.get_opps(avl_opps)
        self.save_logs = save_logs
        self.print_logs = print_logs
        self.to_archer = to_archer

    def get_opps(self, avl_opps):
        return [plan(self.w3) for plan in avl_opps]

    @staticmethod
    def send_to_archer(payload):
        save_file_path = "./logs/archer_api_requests.csv"
        # TODO Include opportunity ID
        response = send2archer(payload)
        data = payload
        data["response"] = response
        with open(save_file_path, "a") as stats_file:
            writer = csv.DictWriter(stats_file, fieldnames=data.keys())
            writer.writerow(data)

        return response

    def process_opps(self, block_number, timestamp, recv_tm, state, gas_prices):
        print("Processing opps")
        for opp in self.opps:
            print(f"Websocket block: {block_number} / API block: {opp.web3.eth.blockNumber}")
            error = None
            archer_response = None

            t0 = time.time()
            opp_response = opp(block_number, timestamp, gas_prices)
            t1 = time.time()
            processing_time_opp = t1 - t0
            processing_time_all = t1 - recv_tm
            if opp_response["status"] == 0:
                print("Not profitable")
                continue
            api_block_number = opp.web3.eth.blockNumber
            if api_block_number != block_number:
                print("API block state is misaligned with Websockets")
                error = "Misaligned block state"
                print("@"*50)
                exit()
            if self.to_archer and opp_response["status"]:
                print("Sending to archer ...")
                archer_response = self.send_to_archer(opp_response["payload"])
                print(archer_response)
                if archer_response.get("status") == "success" and archer_response["most_profitable"]:
                    state["lastProfitTimestamp"] = timestamp
                    if opp_response['profitBeforeGas'] >= state.get("best_profit", 0):
                        state["best_profit"] = opp_response['profitBeforeGas']


            stats = {"wsBlockNumber": block_number,
                     "apiBlockNumber": api_block_number,
                     "blockTimestamp": timestamp, 
                     "receivingTime": int(recv_tm), 
                     "oppProcessingTime": processing_time_opp, 
                     "wholeProcessingTime": processing_time_all,
                     "opportunityFound": opp_response["status"], 
                     "opportunity": str(opp), 
                     "payload": opp_response["payload"], 
                     "profitAfterGas": opp_response["profitAfterGas"],
                     "profitBeforeGas": opp_response["profitBeforeGas"],
                     "rapidGasPrice": gas_prices["rapid"]/10**9, 
                     "archerCallResponse": archer_response, 
                     "error": error, 
                     "sent2archer": self.to_archer and opp_response["status"]
                     }
            if self.save_logs:
                save_logs(stats, cf.save_logs_path)
                

            if self.print_logs:
                stdout_str = f"  BLOCK NUMBER: {block_number}  ".center(80, "#")
                stdout_str += f"\nOPP {opp}: {bool(opp_response['status'])}"
                stdout_str += f"\nRapid gas price: {gas_prices['rapid']:.0f} gwei"
                stdout_str += f"\nTime taken: {processing_time_all:.4f} sec"
                stdout_str += f"\nLatency: {recv_tm-timestamp:.2f} sec"
                stdout_str += f"\nProfit after gas: {opp_response['profitAfterGas']:.4f} ETH"
                stdout_str += f"\nProfit before gas: {opp_response['profitBeforeGas']:.4f} ETH"
                if state.get('lastProfitTimestamp'):
                    stdout_str += f"\nBest profit before gas through archer: {state['best_profit']:.4f} ETH"
                    time_diff = timestamp-state['lastProfitTimestamp']
                    stdout_str += f"\nLast success with archer: {time.strftime('%Hh%Mm%Ss', time.gmtime(time_diff))} ago"
                stdout_str += "\n"+"_"*80
                # os.system("clear")
                print(stdout_str)

        return state


class Listener:

    def __init__(self, w3, opp_manager):
        self.provider = cf.provider(provider_name)
        self.opportunity_manager = opp_manager
        self.w3 = w3

    def header_handler(self, header):
        msg = json.loads(header)["params"]["result"]
        block = int(msg["number"].lstrip("0x"), 16)
        timestamp = int(msg["timestamp"].lstrip("0x"), 16)
        return block, timestamp

    def action(self, w3, recv_tm, storage, gas_prices):
        provider_name = "chainStackUsa"
        w3 = cf.web3_ws_session(provider_name)
        print("action")
        block_number = w3.eth.blockNumber
        print(block_number)
        timestamp = w3.eth.getBlock("latest").timestamp
        print(timestamp)
        print("starting to process opps")
        self.opportunity_manager.process_opps(block_number, timestamp, recv_tm, storage, gas_prices)
        print("finished processing opps")

    def gas_price_updater(self, prices_dict):
        new_prices = fetch_gas_price()
        for k, v in new_prices.items():
            prices_dict[k] = v / 10**9
        return prices_dict

    def run_block_listener(self):
        manager = Manager()
        storage = manager.dict({'rapid': 0, 'fast': 0, 'standard': 0, 'slow': 0, 'timestamp': 0})
        prices = manager.dict()
        prices = self.gas_price_updater(prices)
        last_block_number = 0

        opp_event = gas_price_event = None
        while 1:
            block_num = self.w3.eth.blockNumber
            if last_block_number < block_num:
                last_block_number = block_num
                print(block_num)
                recv_tm = time.time()
                if opp_event: 
                    opp_event.kill()
                opp_event = Process(target=self.action, args=(w3, recv_tm, storage, prices))
                opp_event.start()
            if not gas_price_event:
                gas_price_event = Process(target=self.gas_price_updater, args=(prices,))
                gas_price_event.start()
            time.sleep(2)



if __name__=="__main__":
    avl_opps = [ArbBot]
    provider_name = "chainStackAsia"
    w3 = cf.web3_ws_session(provider_name)
    opp_manager = OpportunityManager(w3, avl_opps)
    listener = Listener(w3, opp_manager)
    listener.run_block_listener()


    