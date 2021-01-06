from arbbot.dt_manager import get_instructions
from arbbot import optimal_amount
import src.config as cf
from src.helpers import round_sig, remove_bytecode_data, tx2bytes
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

    def __init__(self, w3, selection=None, handler_address=cf.address("msqt_dispatcher"), max_input_amount=10**18):
        self.web3 = w3
        self.instr = get_instructions(select=selection)
        self.exchanges = {"uniswap": Uniswap(w3), "sushiswap": SushiSwap(w3)}
        self.gas_price = None
        self.start_time = None
        self.handler_address = handler_address

        self.last_block_timestamp = None
        self.last_block_number = None
        self.max_input_amount = max_input_amount

    def __call__(self, block_number, timestamp, gas_prices):
        self.last_block_number = block_number
        self.last_block_timestamp = timestamp
        self.gas_price = gas_prices["rapid"]
        print("gas price is: ", self.gas_price)
        self.start_time = time.time()
        print("...")

        responses = self.run()
        if responses:
            f_responses = self.format_responses(responses)
            self.save_logs(f_responses, block_number, timestamp)  # Save the logs even if not profitable
            
            max_profit_opp = self.best_profit(responses)
            archer_payload = self.form_payload(max_profit_opp)
            print(f"Instr: {max_profit_opp['instrSymbol']} / Net profit: {max_profit_opp['netProfit']} / Gross profit: {max_profit_opp['grossProfit']}")
            return {"profitAfterGas": max_profit_opp["netProfit"], "payload": archer_payload, "gasAmount": max_profit_opp["gasAmount"], "profitBeforeGas": max_profit_opp["grossProfit"], "status": 1}
        return {"status": 0}

    def __str__(self):
        return "ArbBot"

    def format_responses(self, opps):
        formatted_opps = []
        for r in opps:
            r["netProfit"] = round_sig(r["netProfit"])
            r["grossProfit"] = round_sig(r["grossProfit"])
            r["inputAmount"] = round_sig(r["inputAmount"])
            r["gasCost"] = round_sig(r["gasCost"])
            r["startTime"] = self.start_time
            r["endTime"] = time.time()
            formatted_opps.append(r)

        return formatted_opps
    
    def best_profit(self, opps):
        valid_opps = [o for o in opps if o["inputAmount"]<self.max_input_amount]
        return max(valid_opps, key=lambda x: x["netProfit"])

    @staticmethod
    def calculate_optimized(reserves, fee1, fee2):
        r_p1_t1, r_p1_t2, r_p2_t1, r_p2_t2 = reserves
        params = {"reserveOfToken1InPool1": r_p1_t1, 
                "reserveOfToken2InPool1": r_p1_t2, 
                "reserveOfToken1InPool2": r_p2_t1, 
                "reserveOfToken2InPool2": r_p2_t2, 
                "feeInPool1": fee1,
                "feeInPool2": fee2
                }
        result = optimal_amount.run(params)
        return result

    def check4prof(self, reserves):
        checked_lst = []
        for instr in self.instr:
            tkn1, tkn2, _ = instr.path  # TODO What if tkn3!=tkn1?
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
            gas_cost = instr.gasAmount * self.gas_price / 10**9
            net_profit = gross_profit - gas_cost
            # TODO Repeated info (symbol-id & gasCost-net_profit-gross_profit)
            # TODO Select camel case or underscore and stick to it
            checked_instr = {"instrSymbol": instr.symbol, 
                            "instrId": instr.id, 
                            "inputAmount": optimal_amount["optimal_input_amount"], 
                            "grossProfit": gross_profit, 
                            "netProfit": net_profit, 
                            "gasCost": gas_cost, 
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

    def form_payload(self, opp):
        # Execution script
        # TODO Make instruction fetching more efficient (eg. instructions in dict)
        instr = [i for i in self.instr if i.id==opp["instrId"]][0]  
        tkn_path = [t.address for t in instr.path]
        exchanges = (self.exchanges[instr.pool1.exchange], 
                     self.exchanges[instr.pool2.exchange])
        input_eth_wei = int(opp["inputAmount"] * 10**18)
        args = opp, tkn_path, exchanges, input_eth_wei
        query_script, query_insert_loc = self.form_query_calldata(*args)
        execute_script, execute_insert_loc = self.form_execution_calldata(*args)
        # target_price = int(opp["gasCost"]*10**18 + input_eth_wei)
        target_price = 0  # Archer accounts for the fees
        payload = {
            "bot_id": cf.bot_id,
            "target_block": self.last_block_number+1,
            "trade": execute_script,
            "estimated_profit_before_gas": int(opp["grossProfit"]*10**18),
            "gas_estimate": opp["gasAmount"],
            "query": query_script,
            "query_breakeven": target_price,
            "input_amount": input_eth_wei,
            "input_asset": "ETH",
            "query_insert_locations": query_insert_loc,
            "trade_insert_locations": execute_insert_loc
        }

        return payload


    def form_execution_calldata(self, 
                                opp, 
                                tkn_path, 
                                exchanges_path, 
                                input_eth):
        ## Tx1
        tx1 = exchanges_path[0].swapExactETHForTokens(input_eth, 
                                                 tkn_path[:2], 
                                                 self.handler_address, 
                                                 self.last_block_timestamp)
        ## Tx2
        tx2 = exchanges_path[1].swapExactTokensForETH(293859289444291309581,  # 0xFEE1DEAD0FBADF00D 
                                                 tkn_path[1:], 
                                                 self.handler_address, 
                                                 self.last_block_timestamp)
        # Format txs
        callDataLoc = 2 + 8  # "0x" and 4 bytes for hashed method signature
        tx1_bytes = tx2bytes(tx1["calldata"], tx1["contractAddress"])
        tx2_bytes = tx2bytes(tx2["calldata"], tx2["contractAddress"])
        second_input_location = (len(tx1_bytes)+callDataLoc-2 + 64 + 40)//2  # First tx + contractAddress+calldataLength+locationInCalldata -> in bytes
        # Form a single bytecode
        execute_script = tx1_bytes + tx2_bytes
        execute_script_locations = (second_input_location,)
        
        return execute_script, execute_script_locations


    def form_query_calldata(self, opp, tkn_path, exchange_path, input_eth_wei):
        proxy_contract = self.web3.eth.contract(address=cf.address("uniswapv2_router_proxy"), abi=cf.abi("uniswapv2_router_proxy"))
        # Tx1
        router1 = exchange_path[0].router_address
        args1 = router1, input_eth_wei, tkn_path[0], tkn_path[1]
        tx1_calldata = proxy_contract.encodeABI(fn_name="getOutputAmount", args=args1)
        # Tx2
        router2 = exchange_path[1].router_address
        args2 = router2, 293859289444291309581, tkn_path[1], tkn_path[2]
        tx2_calldata = proxy_contract.encodeABI(fn_name="getOutputAmount", args=args2)
        # Format txs
        callDataLoc = 2 + 8 + 64  # "0x" + 4 bytes for hashed method signature + 32 bytes of router address
        tx1_bytes = tx2bytes(tx1_calldata, proxy_contract.address)
        tx2_bytes = tx2bytes(tx2_calldata, proxy_contract.address)

        second_input_location = (len(tx1_bytes)+callDataLoc-2 + 64 + 40)//2  # First tx + contractAddress+calldataLength+locationInCalldata -> in bytes
        query_script = tx1_bytes + tx2_bytes
        query_script_locations = (second_input_location,)

        return query_script, query_script_locations   


    def save_logs(self, data, block_number, timestamp):
        run_data = {"block_number": block_number, "blockTimestamp": timestamp}
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



