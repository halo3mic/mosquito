from src.helpers import approve_erc20, execute_payload, balance_erc20, erc20_approved
from src.config import provider, address, abi
from src.exchanges import Uniswap, SushiSwap
from src.ganache import Ganache

from pprint import pprint
from web3 import Web3
import pandas as pd
import requests
import atexit
import time


class Simulator:

    def __init__(self, target_block, tkn_path, exchange_path, input_amount, gas_price, provider_name):
        self.target_block = target_block
        self.tkn_path = tkn_path
        self.exchange_path = exchange_path
        self.input_amount = input_amount
        self.gas_price = gas_price

        ganache_session = self.start_gananche_session(target_block, provider_name)
        self.tkn_address = tkn_path[1]
        self.w3 = Web3(Web3.HTTPProvider(ganache_session.node_path))
        self.wallet_address = ganache_session.accounts[0]
        exchange_contracts = {"uniswap": Uniswap(self.w3),
                              "sushiswap": SushiSwap(self.w3)}
        self.exchange_path_contracts = [exchange_contracts[e] for e in self.exchange_path]
        self.routers = {"uniswap": address("uniswapv2_router"), 
                         "sushiswap": address("sushiswap_router")}
        self.block_timestamp = self.w3.eth.getBlock("latest").timestamp
        self.block_number = self.w3.eth.blockNumber

    def execute(self):
        # Record initial state of the account and blocks
        start_state = self.snapshot()
        # Approve
        print("Approving contracts ...")
        approval_receipts = self.execute_approvals()
        # Record intermediate state of the account and blocks (between approvals and trades)
        mid_state = self.snapshot()
        # Execute trades
        print("Executing trades ...")
        trade_receipts = self.execute_trades()
        # Record intermediate state of the account and blocks (between approvals and trades)
        end_state = self.snapshot()
        # Prepare and return results
        results = self.results_manager(start_state, mid_state, end_state, approval_receipts, trade_receipts)
        print("Finished!")

        return results

    @staticmethod
    def results_manager(s1, s2, s3, approval_receipts, trade_receipts):
        if trade_receipts:
            gas_used_trades = sum([t.gasUsed for t in trade_receipts])
        else:
            gas_used_trades = 0
        results = {
                "ethTradeProfit": round(s3['balance_eth'] - s2['balance_eth'], 4), 
                "gasAmountFromTrades": gas_used_trades, 
                    }
        return results

    @staticmethod
    def start_gananche_session(target_block, provider_name):
        provider_path = provider(provider_name).html_path
        start_block_number = target_block-1 if target_block else None
        ganache_session = Ganache(provider_path, block_number=start_block_number)
        ganache_session.start_node()
        atexit.register(lambda: ganache_session.kill())  # Closes the node after python session is finished

        return ganache_session

    def snapshot(self):
        state = {"block_timestamp": self.w3.eth.getBlock("latest").timestamp,
                "block_number": self.w3.eth.blockNumber,
                "balance_eth": self.w3.eth.getBalance(self.wallet_address)/10**18,
                "balance_tkn": balance_erc20(self.w3, self.wallet_address, self.tkn_address)}
        return state

    def execute_approvals(self):
        spenders = (self.routers[self.exchange_path[1]],)
        txs = (approve_erc20(self.tkn_address, s) for s in spenders)
        tx_hashes = [execute_payload(self.w3, t, self.wallet_address, gas_price=self.gas_price) for t in txs]
        results = [self.w3.eth.waitForTransactionReceipt(h) for h in tx_hashes]

        return results

    def execute_trades(self):
        try:
            # Trade ETH for token
            tkn_path1 = self.tkn_path[:2]
            eth_input_amount = self.input_amount
            swap_payload1 = self.exchange_path_contracts[0].swapExactETHForTokens(eth_input_amount, 0, tkn_path1, self.wallet_address, self.block_timestamp)
            tx_hash = execute_payload(self.w3, swap_payload1, self.wallet_address, gas_price=self.gas_price)
            trade1_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
            # Trade token for ETH
            tkn_path2 = self.tkn_path[1:]
            tkn_input_amount = balance_erc20(self.w3, self.wallet_address, self.tkn_address) * (1-0.0001) * 10**18
            swap_payload2 = self.exchange_path_contracts[1].swapExactTokensForETH(tkn_input_amount, 0, tkn_path2, self.wallet_address, self.block_timestamp)
            tx_hash = execute_payload(self.w3, swap_payload2, self.wallet_address, gas_price=self.gas_price)
            trade2_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)

            return trade1_receipt, trade2_receipt
        except Exception as e:
            print(repr(e))

    def query(self):
        router1 = self.routers[self.exchange_path[0]]
        router2 = self.routers[self.exchange_path[1]]
        tkn_path1 = self.tkn_path[:2]
        tkn_path2 = self.tkn_path[1:]
        eth_input_amount = int(self.input_amount)

        tkn_amount = self.get_amount_out(router1, eth_input_amount, *tkn_path1)
        eth_output_amount = self.get_amount_out(router2, tkn_amount, *tkn_path2)
        result = {"profitable": eth_output_amount > eth_input_amount, 
                  "profit": (eth_output_amount - eth_input_amount)/10**18}

        return result


    def get_amount_out(self, router_address, input_amount, from_token, to_token):
        uniswapv2_proxy_address = "0x121835e15703a1a7bab32626d0927D60F90A81D7"
        proxy_contract = self.w3.eth.contract(address=uniswapv2_proxy_address, abi=abi("uniswapv2_proxy"))
        amount_out = proxy_contract.functions.getOutputAmount(router_address, input_amount, from_token, to_token).call()
        return amount_out

    # def get_amount_out(self, router_address, input_amount, from_token, to_token):
    #     print(self.w3.eth.blockNumber)
    #     proxy_contract = self.w3.eth.contract(address=router_address, abi=abi("uniswapv2_router"))
    #     _, amount_out = proxy_contract.functions.getAmountsOut(input_amount, [from_token, to_token]).call()
    #     return amount_out


def validate_opportunity_found(block_number, instruction_id, provider_name):

    def compare(opp, execution, query):
        comp = {"gasAmountDiff": round(execution["gasAmountFromTrades"]-opp["gasAmount"], 4), 
                "netProfitDiff": round(execution["ethTradeProfit"]-opp["netProfit"], 4), 
                "grossProfitDiff": round(query["profit"]-opp["grossProfit"]),
                "queryProfitable": query["profitable"]
                }
        together = {**opp, **execution, **comp}
        return together

    print("Fetching opportunity info ...")
    params, opp_info = fetch_opp_info(block_number, instruction_id)
    simulator = Simulator(*params, provider_name)
    query_result = simulator.query()
    execution_info = simulator.execute()
    comparison = compare(opp_info, execution_info, query_result)

    return comparison


def fetch_opp_info(block_number, instruction_id):
    logs_path = "./logs/arbbot.csv"
    tkns_path = "./config/tokens.csv"
    instr_path = "./config/instructions.csv"
    pools_path = "./config/pools.csv"
    logs_df = pd.read_csv(logs_path)
    tkns_df = pd.read_csv(tkns_path)
    instr_df = pd.read_csv(instr_path)
    pools_df = pd.read_csv(pools_path)

    opp = logs_df[(logs_df["blockNumber"]==block_number) & (logs_df["instrName"]==instruction_id)].iloc[0]
    instr = instr_df[instr_df.id==opp.instrId].iloc[0]

    target_block = block_number
    tkn_path = [tkns_df[tkns_df.id==t].address.iloc[0] for t in instr.path.split(", ")]
    exchange_path = [pools_df[pools_df.id==p].exchange.iloc[0] for p in (instr.pool1, instr.pool2)]
    input_amount = opp.optimalAmount * 10**18
    gas_price = int(opp.gasCost / opp.gasAmount * 10**9)
    params = target_block, tkn_path, exchange_path, input_amount, gas_price
    info = {"grossProfit": opp.grossProfit, "netProfit": opp.netProfit, "gasAmount": opp.gasAmount}

    return params, info


if __name__ == "__main__":
    block_number = 11534461
    instr_name = "weth2link2weth_sushiswap2Uniswap"
    provider_name = "alchemy"

    r = validate_opportunity_found(block_number, instr_name, provider_name)

    print("#"*60)
    pprint(r)









