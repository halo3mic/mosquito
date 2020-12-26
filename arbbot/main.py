from arbbot.dt_manager import get_instructions
from arbbot import optimal_amount
import src.config as cf
from src.helpers import round_sig
from src.exchanges import Uniswap, SushiSwap
from src.gas_manager import fetch_gas_price

from concurrent.futures import ThreadPoolExecutor
import csv
import websockets
from multiprocessing import Process
import asyncio
import time
import json

from pprint import pprint


class ArbBot:

    save_logs_path = "./logs/arbbot.csv"

    def __init__(self, w3, selection=None):
        self.web3 = w3
        self.instr = get_instructions(select=selection)
        self.exchanges = {"uniswap": Uniswap(w3), "sushiswap": SushiSwap(w3)}
        self.gas_price = 10**9  # Default is huge gas
        self.gas_amount = 260000  # Associate this with the instruction

    def __call__(self, block_number, timestamp):
        print("...")
        self.last_timestamp = time.time()
        responses = self.run_async(self.web3)
        profitables = self.response_manager(responses)
        print(f"Gas price: {self.gas_price/10**9} gwei")
        self.save_logs(profitables, block_number, timestamp)  # Save the logs even if not profitable
        if profitables:
            pprint(profitables)
            max_profit = self.best_profit(profitables)
            return {"profit": max_profit, "byteload": "", "status": 1}
        return {"profit": 0, "byteload": "", "status": 0}

    def __str__(self):
        return "ArbBot"

    def response_manager(self, responses):
        profitable_opps = []
        for r in responses:
            name, results = r
            profit = 0
            if results[0]["arb_available"]:
                profit = results[0]["estimated_output_amount"] - results[0]["optimal_input_amount"]
                name = name+"_o" 
            if results[1]["arb_available"]:
                profit = results[1]["estimated_output_amount"] - results[1]["optimal_input_amount"]
                name =  name+"_r"
            gas_cost = self.gas_price * self.gas_amount / 10**18
            print(gas_cost)
            profit -= gas_cost
            if profit > 0:
                profitable_opps.append({"name": name+"_r", "profit": round_sig(profit), "inputAmount": round_sig(results[1]["optimal_input_amount"]), "gas_cost": gas_cost})

        return profitable_opps
    
    @staticmethod
    def best_profit(opps):
        return max(opp["profit"] for opp in opps)

    def fetch_reserves(self, atm_opp):
        pool1, pool2 = atm_opp.pool1, atm_opp.pool2
        ex1 = self.exchanges[pool1.exchange]
        ex2 = self.exchanges[pool2.exchange]

        *reserve_pool1, _ = ex1.get_reserves(pool1.address)
        *reserve_pool2, _ = ex2.get_reserves(pool2.address)
        reserve_pool1_tkn1 = reserve_pool1[atm_opp.tkn1]/10**(pool1.tokens[atm_opp.tkn1].decimal)
        reserve_pool1_tkn2 = reserve_pool1[atm_opp.tkn2]/10**(pool1.tokens[atm_opp.tkn2].decimal)
        reserve_pool2_tkn1 = reserve_pool2[atm_opp.tkn1]/10**(pool2.tokens[atm_opp.tkn1].decimal) 
        reserve_pool2_tkn2 = reserve_pool2[atm_opp.tkn2]/10**(pool2.tokens[atm_opp.tkn2].decimal)

        return reserve_pool1_tkn1, reserve_pool1_tkn2, reserve_pool2_tkn1, reserve_pool2_tkn2

    @staticmethod
    def calculate_optimized(params):
        result1 = optimal_amount.run(params)
        result2 = optimal_amount.run(params, reverse=1)

        return result1, result2

    def check4prof(self, instr):
        r_p1_t1, r_p1_t2, r_p2_t1, r_p2_t2 = self.fetch_reserves(instr)
        params = {"reserveOfToken1InPool1": r_p1_t2, 
                "reserveOfToken2InPool1": r_p1_t1, 
                "reserveOfToken1InPool2": r_p2_t2, 
                "reserveOfToken2InPool2": r_p2_t1, 
                "feeInPool1": instr.pool1.fee,
                "feeInPool2": instr.pool2.fee
                }
        optimal_amount = self.calculate_optimized(params)

        return atm_opp.symbol, optimal_amount

    def run_async(self, atm_opps):
        with ThreadPoolExecutor() as executor:
            responses = executor.map(self.check4prof, self.instr)
            gas_price = executor.submit(self.get_gas_price)
        self.gas_price = gas_price.result()
        return responses

    def save_logs(self, data, block_number, timestamp):
        time_now = int(time.time())
        run_data = {"block_number": block_number, "blockTimestamp": timestamp, "finishTimestamp": time_now}
        columns = list(run_data.keys()) + list(data[0].keys())
        with open(self.save_logs_path, "a") as stats_file:
            writer = csv.DictWriter(stats_file, fieldnames=columns)
            for row in data:
                full_row = {**row, **run_data}
                writer.writerow(full_row)

    def import_state(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def export_state(self):
        return {"amt_opps": self.atm_opps, "exchanges": self.exchanges}

    @staticmethod
    def get_gas_price():
        r = fetch_gas_price()
        rapid_gas = r["rapid"]
        return rapid_gas

if __name__ == "__main__":
    provider_name = "chainStackBlocklytics"
    provider = cf.provider(provider_name)
    w3 = cf.web3_api_session(provider_name)
    bot = ArbBot(w3)
    r = bot(1, 1)
    pprint(r)
    # run_block_listener(provider, bot)



