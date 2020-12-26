from arbbot.dt_manager import get_instructions
from arbbot import optimal_amount
import src.config as cf
from src.helpers import round_sig
from src.exchanges import Uniswap, SushiSwap

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
        self.gas_price = None
        self.start_time = None

    def __call__(self, block_number, timestamp, gas_prices):
        self.gas_price = gas_prices["rapid"]
        self.start_time = time.time()
        print("...")

        responses = self.run()
        if responses:
            f_responses = self.format_responses(responses)
            self.save_logs(f_responses, block_number, timestamp)  # Save the logs even if not profitable
            
            max_profit_opp = self.best_profit(responses)
            if max_profit_opp["net_profit"] > 0:
                bytecode = ""  # TODO make bytecode
                pprint(max_profit_opp)
                return {"profit": max_profit_opp["net_profit"], "bytecode": bytecode, "gasAmount": max_profit_opp["gasAmount"], "status": 1}
        return {"profit": 0, "bytecode": "", "status": 0}

    def __str__(self):
        return "ArbBot"

    def format_responses(self, opps):
        formatted_opps = []
        for r in opps:
            r["net_profit"] = round_sig(r["net_profit"])
            r["gross_profit"] = round_sig(r["gross_profit"])
            r["input_amount"] = round_sig(r["input_amount"])
            r["gas_cost"] = round_sig(r["gas_cost"])
            r["finish_time"] = time.time()
            r["start_time"] = self.start_time
            formatted_opps.append(r)

        return formatted_opps
    
    @staticmethod
    def best_profit(opps):
        return max(opps, key=lambda x: x["net_profit"])


    @staticmethod
    def calculate_optimized(reserves, fee1, fee2):
        r_p1_t1, r_p1_t2, r_p2_t1, r_p2_t2 = reserves
        params = {"reserveOfToken1InPool1": r_p1_t2, 
                "reserveOfToken2InPool1": r_p1_t1, 
                "reserveOfToken1InPool2": r_p2_t2, 
                "reserveOfToken2InPool2": r_p2_t1, 
                "feeInPool1": fee1,
                "feeInPool2": fee2
                }
        return optimal_amount.run(params)

    def check4prof(self, reserves):
        checked_lst = []
        for instr in self.instr:
            tkn1, tkn2, tkn3 = instr.path
            r_p1_t1 = reserves[instr.pool1.id][tkn1.id] / 10**(tkn1.decimal)
            r_p1_t2 = reserves[instr.pool1.id][tkn2.id] / 10**(tkn2.decimal) 
            r_p2_t1 = reserves[instr.pool2.id][tkn1.id] / 10**(tkn1.decimal) 
            r_p2_t2 = reserves[instr.pool2.id][tkn2.id] / 10**(tkn2.decimal)
            calc_reserves = r_p1_t1, r_p1_t2, r_p2_t1, r_p2_t2
            fee1, fee2 = instr.pool1.fee, instr.pool2.fee
            optimal_amount = self.calculate_optimized(calc_reserves, fee1, fee2)

            if not optimal_amount["arb_available"]:
                continue
            gross_profit = optimal_amount["estimated_output_amount"] - optimal_amount["optimal_input_amount"]
            gas_cost = instr.gasAmount * self.gas_price / 10**18
            net_profit = gross_profit - gas_cost

            checked_instr = {"symbol": instr.symbol, 
                            "id": instr.id, 
                            "input_amount": optimal_amount["optimal_input_amount"], 
                            "gross_profit": gross_profit, 
                            "net_profit": net_profit, 
                            "gas_cost": gas_cost, 
                            "gasAmount": instr.gasAmount
                            }
            checked_lst.append(checked_instr)

        return checked_lst

    def async_fetch_reserves(self):
        # Remove all duplicates
        all_pools = []
        for pool in (p for i in self.instr for p in (i.pool1, i.pool2)):
            if pool not in all_pools:
                all_pools.append(pool)
        # Thread for each web3 call
        with ThreadPoolExecutor() as executor:
            reserves = executor.map(self.fetch_reserves, all_pools)
        reserves_dict = dict(reserves)
        return reserves_dict

    def fetch_reserves(self, pool):
        exchange_contract = self.exchanges[pool.exchange]
        *reserve_per_tkn, _ = exchange_contract.get_reserves(pool.address)
        reserve = dict((pool.tokens[i], reserve_per_tkn[i]) for i in range(len(reserve_per_tkn)))
        return pool.id, reserve

    def run(self):
        reserves = self.async_fetch_reserves()
        opps = self.check4prof(reserves)
        return opps

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
        return {"amt_opps": self.instr, "exchanges": self.exchanges}


if __name__ == "__main__":
    provider_name = "chainStackBlocklytics"
    provider = cf.provider(provider_name)
    w3 = cf.web3_api_session(provider_name)
    bot = ArbBot(w3)
    r = bot(1, 1)
    pprint(r)
    # run_block_listener(provider, bot)



