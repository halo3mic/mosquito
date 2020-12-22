from arbbot.opp_checker import main_async
from arbbot.dt_manager import get_atm_opps
from arbbot import optimal_amount
import src.config as cf
from src.helpers import round_sig
from src.exchanges import Uniswap, SushiSwap

from concurrent.futures import ThreadPoolExecutor
import csv
import websockets
from multiprocessing import Process, Queue
import asyncio
import time
import json

from pprint import pprint


class ArbBot:

    save_logs_path = "./logs/arbbot.csv"

    def __init__(self, w3, selection=None):
        self.web3 = w3
        self.atm_opps = get_atm_opps(select=selection)
        self.exchanges = {"uniswap": Uniswap(w3), "sushiswap": SushiSwap(w3)}

    def __call__(self, block_number, timestamp):
        print("...")
        self.last_timestamp = time.time()
        responses = self.calculate_async(self.web3)
        profitables = self.response_manager(responses)
        print("***")
        if profitables:
            pprint(profitables)
            self.save_logs(profitables, block_number)
            total_profit = self.sum_profits(profitables)
            return total_profit

    def __str__(self):
        return "ArbBot"

    def response_manager(self, responses):
        profitable_opps = []
        for r in responses:
            name, results = r
            if results[0]["arb_available"]:
                profit = results[0]["estimated_output_amount"] - results[0]["optimal_input_amount"]
                profitable_opps.append({"name": name+"_o", "profit": round_sig(profit)})
            if results[1]["arb_available"]:
                profit = results[1]["estimated_output_amount"] - results[1]["optimal_input_amount"]
                profitable_opps.append({"name": name+"_r", "profit": round_sig(profit)})

        return profitable_opps
    
    @staticmethod
    def sum_profits(opps):
        return sum(opp["profit"] for opp in opps)

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

    def check4prof(self, atm_opp):
        t0 = time.time()
        r_p1_t1, r_p1_t2, r_p2_t1, r_p2_t2 = self.fetch_reserves(atm_opp)
        t1 = time.time()
        print(f"Fetching reserves took: {t1-t0:.2f}")
        params = {"reserveOfToken1InPool1": r_p1_t2, 
                "reserveOfToken2InPool1": r_p1_t1, 
                "reserveOfToken1InPool2": r_p2_t2, 
                "reserveOfToken2InPool2": r_p2_t1, 
                "feeInPool1": atm_opp.pool1.fee,
                "feeInPool2": atm_opp.pool2.fee
                }
        optimimal_amount = self.calculate_optimized(params)

        return atm_opp.symbol, optimimal_amount

    def calculate_async(self, atm_opps):
        with ThreadPoolExecutor() as executor:
            responses = executor.map(self.check4prof, self.atm_opps)
        return responses

    def save_logs(self, data, block_number):
        columns = ["block"] + list(data[0].keys())
        with open(self.save_logs_path, "a") as stats_file:
            writer = csv.DictWriter(stats_file, fieldnames=columns)
            for row in data:
                writer.writerow(row)

    def import_state(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def export_state(self):
        return {"amt_opps": self.atm_opps, "exchanges": self.exchanges}


if __name__ == "__main__":
    provider_name = "alchemy"
    provider = cf.provider(provider_name)
    w3 = cf.web3_api_session(provider_name)
    bot = ArbBot(w3)
    # run_block_listener(provider, bot)



