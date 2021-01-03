from src.helpers import approve_erc20, execute_payload, balance_erc20, erc20_approved
from arbbot.dt_manager import get_instructions 
from src.config import provider, address, abi
from src.exchanges import Uniswap, SushiSwap
from src.ganache import Ganache
from arbbot.main import ArbBot

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

    def results_manager(self, s1, s2, s3, approval_receipts, trade_receipts):
        if trade_receipts:
            gas_used_trades = sum([t.gasUsed for t in trade_receipts])
        else:
            gas_used_trades = 0
        results = {
                "endTknBalance": balance_erc20(self.w3, self.wallet_address, self.tkn_address, convert=True),
                "ethTradeProfit": round(s3['balance_eth'] - s2['balance_eth'], 4), 
                "gasAmountFromTrades": gas_used_trades, 
                    }
        return results

    @staticmethod
    def start_gananche_session(target_block, provider_name):
        unlocked = [address("archerDAOClient"), "0xB96f132Ad2E293A47619ec34b9D090Cfe9735820", address("calebsDispatcher")]
        provider_path = provider(provider_name).html_path
        start_block_number = target_block if target_block else None
        ganache_session = Ganache(provider_path, block_number=start_block_number, mine_interval=3, unlock=unlocked)
        ganache_session.start_node()
        atexit.register(lambda: ganache_session.kill())  # Closes the node after python session is finished

        return ganache_session

    def snapshot(self):
        state = {
                # "block_timestamp": self.w3.eth.getBlock("latest").timestamp,
                "block_number": self.w3.eth.blockNumber,
                "balance_eth": self.w3.eth.getBalance(self.wallet_address)/10**18,
                "balance_tkn": balance_erc20(self.w3, self.wallet_address, self.tkn_address, convert=True)
                }
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
            swap_payload1 = self.exchange_path_contracts[0].swapExactETHForTokens(eth_input_amount, tkn_path1, self.wallet_address, self.block_timestamp)
            pprint(swap_payload1["calldata"])
            tx_hash = execute_payload(self.w3, swap_payload1, self.wallet_address, gas_price=self.gas_price)
            trade1_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
            # Trade token for ETH
            tkn_path2 = self.tkn_path[1:]
            tkn_input_amount = balance_erc20(self.w3, self.wallet_address, self.tkn_address)
            swap_payload2 = self.exchange_path_contracts[1].swapExactTokensForETH(tkn_input_amount, tkn_path2, self.wallet_address, self.block_timestamp)
            pprint(swap_payload2["calldata"])
            tx_hash = execute_payload(self.w3, swap_payload2, self.wallet_address, gas_price=self.gas_price)
            trade2_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)

            return trade1_receipt, trade2_receipt
        except Exception as e:
            print(repr(e))
            raise e

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
        proxy_contract = self.w3.eth.contract(address=uniswapv2_proxy_address, abi=abi("uniswapv2_router_proxy"))
        amount_out = proxy_contract.functions.getOutputAmount(router_address, input_amount, from_token, to_token).call()
        return amount_out

    # def get_amount_out(self, router_address, input_amount, from_token, to_token):
    #     print(self.w3.eth.blockNumber)
    #     proxy_contract = self.w3.eth.contract(address=router_address, abi=abi("uniswapv2_router"))
    #     _, amount_out = proxy_contract.functions.getAmountsOut(input_amount, [from_token, to_token]).call()
    #     return amount_out

    def query_all_prices(self, script, inputLocations):
        contract = self.w3.eth.contract(abi=abi("dispatcher_queryEngine"), address=address("dispatcher_queryEngine"))
        r = contract.functions.queryAllPrices(script, inputLocations).call()
        r = r.hex()
        print(r)
        r = [r[i:i+64] for i in range(0,len(r),64)]
        return r

    def run_arbbot(self):
        bot = ArbBot(self.w3)
        gas_prices = {"rapid": self.gas_price}
        r = bot(self.block_number, self.block_timestamp, gas_prices)
        return r

    def simple_make_trade_test(self):
        calldata = "7a250d5630B4cF539739dF2C5dAcb4c659F2488D00000000000000000000000000000000000000000000000000000000000000e47ff36ab500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000080000000000000000000000000c53A5828a02334CEFbCc69EfD617F01cF6cc3B98000000000000000000000000000000000000000000000000000000005feaad0d0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000001ceb5cb57c4d4e2b2433641b95dd330a33185a44d9e1cE17f2641f24aE83637ab66a2cca9C378B9F000000000000000000000000000000000000000000000000000000000000010418cbafe5000000000000000000000000000000000000000000000003e10536068a2ab128000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000c53A5828a02334CEFbCc69EfD617F01cF6cc3B98000000000000000000000000000000000000000000000000000000005feaad0d00000000000000000000000000000000000000000000000000000000000000020000000000000000000000001ceb5cb57c4d4e2b2433641b95dd330a33185a44000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        eth_value = int(28.05*10**18)
        self.eth2dispatcher("0xB96f132Ad2E293A47619ec34b9D090Cfe9735820", address("calebsDispatcher"), 200)
        dispatcher = self.w3.eth.contract(abi=abi("dispatcher"), address=address("calebsDispatcher"))
        self.approve_tkn4dispatcher(dispatcher, self.tkn_address)
        
        # self.execute_maketrade(dispatcher.address, calldata, eth_value)
        tx_hash = dispatcher.functions.makeTrade(calldata, eth_value).transact({"gasPrice": self.gas_price, "gas": 2000000, "from": "0xB96f132Ad2E293A47619ec34b9D090Cfe9735820"})
        r = self.w3.eth.waitForTransactionReceipt(tx_hash)
        if r.status == 0:
            raise Exception("MakeTrade failed")
        else:
            print(self.w3.eth.getBalance(address("calebsDispatcher")))
        print("Dispatcher final eth balance: ", self.w3.eth.getBalance(address("calebsDispatcher"))/10**18)
        print("Dispatcher final tkn balance: ", balance_erc20(self.w3, dispatcher.address, "0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44", convert=1))


    # def make_trade_full_test(self):
    #     dispatcher_address = address("calebsDispatcher")
    #     client_address = address("archerDAOClient")

    #     dispatcher = self.w3.eth.contract(abi=abi("dispatcher"), address=dispatcher_address)
    #     opp = self.get_arbbot_opp(dispatcher.address)
    #     _, decoded = dispatcher.decode_function_input(opp["bytecode"])

    #     self.eth2dispatcher(client_address, dispatcher.address, 200)
    #     self.approve_tkn4dispatcher(dispatcher, self.tkn_address)
    #     print("Executing ... ")
    #     args = decoded["queryScript"], decoded["queryInputLocations"], decoded["executeScript"], decoded["executeInputLocations"], decoded["targetPrice"], decoded["ethValue"]
    #     tx_hash = dispatcher.functions.makeTrade(*args).transact({"gasPrice": self.gas_price, "gas": 2000000, "from": client_address})
    #     r = self.w3.eth.waitForTransactionReceipt(tx_hash)
    #     if r.status == 0:
    #         raise Exception("MakeTrade failed")

    #     print("Dispatcher final eth balance: ", self.w3.eth.getBalance(dispatcher.address)/10**18)
    #     print("Dispatcher final tkn balance: ", balance_erc20(self.w3, dispatcher.address, self.tkn_address, convert=1))

    def make_trade_full_test(self):
        dispatcher_address = address("calebsDispatcher")
        client_address = address("archerDAOClient")

        dispatcher = self.w3.eth.contract(abi=abi("dispatcher"), address=dispatcher_address)
        opp = self.get_arbbot_opp(dispatcher.address)

        self.eth2dispatcher(client_address, dispatcher.address, 200)
        self.approve_tkn4dispatcher(dispatcher, self.tkn_address)

        print("Executing ... ")
        #  _, decoded = dispatcher.decode_function_input(opp["bytecode"])
        # args = decoded["queryScript"], decoded["queryInputLocations"], decoded["executeScript"], decoded["executeInputLocations"], decoded["targetPrice"], decoded["ethValue"]
        payload = opp["payload"]
        pprint(payload)
        args = payload["query"], payload["query_insert_locations"], payload["trade"], payload["trade_insert_locations"], payload["query_breakeven"], payload["input_amount"]
        tx_hash = dispatcher.functions.makeTrade(*args).transact({"gasPrice": self.gas_price, "gas": 2000000, "from": client_address})
        # tx = {"gasPrice": self.gas_price, "gas": 2000000, "from": client_address, "to": dispatcher.address, "data": opp["bytecode"]}
        # tx_hash = self.w3.eth.sendTransaction(tx)
        r = self.w3.eth.waitForTransactionReceipt(tx_hash)
        if r.status == 0:
            raise Exception("makeTrade failed")

        print("Dispatcher final eth balance: ", self.w3.eth.getBalance(dispatcher.address)/10**18)
        print("Dispatcher final tkn balance: ", balance_erc20(self.w3, dispatcher.address, self.tkn_address, convert=1))

    def get_arbbot_opp(self, handler):
        bot = ArbBot(self.w3, handler_address=handler)
        gas_prices = {"rapid": self.gas_price}
        response = bot(self.block_number, self.block_timestamp, gas_prices)
        return response
        

    def approve_tkn4dispatcher(self, dispatcher, tkn_address):
        router_address = self.exchange_path_contracts[1].router_address
        tx = dispatcher.functions.tokenAllowAll([tkn_address], router_address).transact({"from": "0xB96f132Ad2E293A47619ec34b9D090Cfe9735820", "gasPrice": self.gas_price, "gas": 200000}).hex()
        r = self.w3.eth.waitForTransactionReceipt(tx)
        if r.status == 0:
            raise Exception("Approval failed")
        approved_amount = erc20_approved(self.w3, tkn_address, dispatcher.address, router_address, convert=1)
        print(f"Router can now take {approved_amount} tokens ({tkn_address}) from dispatcher")

    def eth2dispatcher(self, sender, dispatcher, val):
        # Send money to dispatcher
        print('balance of wallet:', self.w3.eth.getBalance(self.wallet_address))
        tx_transfer = {"from": self.wallet_address, "to": sender, "value": (val+1)*10**18}
        transfer_hash = self.w3.eth.sendTransaction(tx_transfer).hex()
        self.w3.eth.waitForTransactionReceipt(transfer_hash)
        print('balance of wallet:', self.w3.eth.getBalance(self.wallet_address))
        print('balance of client:', self.w3.eth.getBalance(sender))
        tx_transfer = {"from": sender, "to": dispatcher, "value": val*10**18}
        transfer_hash = self.w3.eth.sendTransaction(tx_transfer).hex()
        self.w3.eth.waitForTransactionReceipt(transfer_hash)
        print('balance of client:', self.w3.eth.getBalance(sender))
        print('balance of dispatcher:', self.w3.eth.getBalance(dispatcher))

    def execute_maketrade(self, from_address, script, ethValue):
        def address_at(script, location):
            return script[location:location+40]


        def uint256_at(script, location):
            return int(script[location:location+64], 16)*2

        def call_method(contract_address, calldata, eth_value):
            contract_address = Web3.toChecksumAddress(contract_address)
            calldata = "0x" + calldata

            tx = {
                "data": calldata, 
                "value": eth_value, 
                "to": contract_address, 
                "from": from_address,
                "gas": 2000000, 
                "gasPrice": 100
                }
            tx_hash = self.w3.eth.sendTransaction(tx).hex()
            receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
            if receipt.status==0:
                raise Exception("Trade tx failed")
            else:
                print("Dispatcher eth balance: ", self.w3.eth.getBalance(address("calebsDispatcher"))/10**18)
                print("Dispatcher tkn balance: ", balance_erc20(self.w3, from_address, "0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44", convert=1))
                # pprint(calldata)
                # pprint(receipt)

        location = 0
        while (location < len(script)):
            contractAddress = address_at(script, location)
            calldataLength = uint256_at(script, location + 40)
            calldataStart = location + 40 + 64
            callData = script[calldataStart:calldataStart+calldataLength]
            if location == 0:
                call_method(contractAddress, callData, ethValue)
            else:
                call_method(contractAddress, callData, 0)
            location += (40 + 64 + calldataLength)

def results_manager(opp, execution, query):
    comp = {
            "gasAmountDiff": round(execution["gasAmountFromTrades"]-opp["gasAmount"], 4), 
            "netProfitDiff": round(execution["ethTradeProfit"]-opp["netProfit"], 4), 
            "grossProfitDiff": round(query["profit"]-opp["grossProfit"], 4),
            "queryProfitable": query["profitable"]
            }
    together = {**opp, **execution, **comp}
    del together["instruction"]
    return together


def validate_opportunity_found(block_number, instruction_id, provider_name):
    print("Fetching opportunity info ...")
    params, opp_info = fetch_opp_info(block_number, instruction_id)
    simulator = Simulator(*params, provider_name)

    # bot_results = simulator.run_arbbot()
    # pprint(bot_results)
    query_result = simulator.query()
    execution_info = simulator.execute()  
    results = results_manager(opp_info, execution_info, query_result)

    return results

def simulate_sending2archer(block_number, instruction_id, provider_name):
    params, _ = fetch_opp_info(block_number, instruction_id)
    # instructions = get_instructions()
    simulator = Simulator(*params, provider_name)
    # to_archer = simulator.send2archer(instructions)
    # simulator.simple_make_trade_test()
    simulator.make_trade_full_test()

    # return to_archer

def fetch_opp_info(block_number, instruction_id):
    logs_path = "./logs/arbbot.csv"
    tkns_path = "./config/tokens.csv"
    instr_path = "./config/instructions.csv"
    pools_path = "./config/pools.csv"
    logs_df = pd.read_csv(logs_path)
    tkns_df = pd.read_csv(tkns_path)
    instr_df = pd.read_csv(instr_path)
    pools_df = pd.read_csv(pools_path)
    # pprint(logs_df[logs_df.netProfit>0].sort_values(by="blockNumber", ascending=0).head())
    opp = logs_df[(logs_df["blockNumber"]==block_number) & (logs_df["instrName"]==instruction_id)].iloc[0]
    instr = instr_df[instr_df.id==opp.instrId].iloc[0]

    target_block = block_number
    tkn_path = [tkns_df[tkns_df.id==t].address.iloc[0] for t in instr.path.split(", ")]
    exchange_path = [pools_df[pools_df.id==p].exchange.iloc[0] for p in (instr.pool1, instr.pool2)]
    input_amount = opp.optimalAmount * 10**18
    gas_price = round(opp.gasCost / opp.gasAmount * 10**9)
    params = target_block, tkn_path, exchange_path, input_amount, gas_price
    info = {"grossProfit": opp.grossProfit, "netProfit": opp.netProfit, "gasAmount": opp.gasAmount, "instruction": instr}

    return params, info


if __name__ == "__main__":
    block_number = 11581169
    instr_name = "weth2kp3rweth_sushiswap2Uniswap"
    provider_name = "alchemy"
    

    r = validate_opportunity_found(block_number, instr_name, provider_name)
    # r = simulate_sending2archer(block_number, instr_name, provider_name)
    print("#"*60)
    pprint(r)









