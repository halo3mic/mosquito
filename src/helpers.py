from src.config import *
import time
import atexit
import codecs


class Uniswap:


    def __init__(self, web3):
        self.web3 = web3
        self.fee = 0.003
        
    def get_amount_out(self, input_amount, pool_address, inverse=False):
        pool_contract = self.web3.eth.contract(address=pool_address, abi=ABIS["uniswapv2"])
        bal0, bal1, _ = pool_contract.functions.getReserves().call()
        if inverse: bal0, bal1 = bal1, bal0
        # bal0 /= 10**decimals[0]
        # bal1 /= 10**decimals[1]
        amount_out = (1 - bal1/(bal1+input_amount)) * bal0 * (1-self.fee)
        
        return amount_out

    def get_payload(self, input_amount, amount_out, path, gas_limit, to_address, tkn_slippage=0.01, time_slippage=300):
        router_address = ADDRESSES["uniswap"]["uniswapv2_router02"]
        router_contract = self.web3.eth.contract(address=router_address, abi=ABIS["uniswapv2_router02"])
        function = "swapExactTokensForETH"
        timestamp = self.web3.eth.getBlock('latest')["timestamp"]
        args = [int(input_amount), int(amount_out*(1-tkn_slippage)), path, to_address, timestamp+time_slippage]
        calldata = router_contract.encodeABI(fn_name=function, args=args)
        payload = {"contractAddress": router_address, 
                   "calldata": calldata,
                   "gasLimit": gas_limit
                  }

        return payload


def approve_erc20(token_address, spender, amount=-1):
    amount = "f"*64 if amount==-1 else hex(amount).split("x")[1]
    calldata = "0x095ea7b3" + spender.lower().split("x")[1].zfill(64) + amount.zfill(64)
    payload = {"contractAddress": token_address, 
               "calldata": calldata, 
               "gasLimit": 70000}
    return payload


def transfer_erc20(token_address, reciver, amount):
    calldata = "0xa9059cbb" + reciver.lower().split("x")[1].zfill(64) + hex(amount).split("x")[1].zfill(64)
    payload = {"contractAddress": token_address, 
               "calldata": calldata, 
               "gasLimit": 50000}
    return payload


def balance_erc20(w3, holder_address, token_address):
    tkn_contract = w3.eth.contract(address=token_address, abi=ABIS["erc20_token"])
    decimals = tkn_contract.functions.decimals().call()
    balance = tkn_contract.functions.balanceOf(holder_address).call()
    return balance / 10**decimals


def str2hex(text):
    return codecs.encode(text.encode(), "hex").decode()


def int2hex(digit):
    return format(int(digit), "x")


def prepare(arg, atype):
    methods = {"a": lambda x: x.split("x")[1].zfill(64), 
               "i": lambda x: int2hex(x).zfill(64), 
               "s": lambda x: str2hex(x).zfill(64)}
    return methods[atype](arg)


def payload2bytes(payload):
    args = [("botId", "s"), 
            ("supplierAddress", "a"), 
            ("blockNumber", "i"), 
            ("gasEstimate", "i"), 
            ("estimatedProfit", "i"), 
            ("profitCurrency", "s")]
    
    byteload = ""
    for key, atype in args:
        byteload += prepare(payload[key], atype)
    byteload += prepare(len(payload["txs"]), "i")

    for tx in payload["txs"]:
        calldata = tx["calldata"].split("x")[1]
        calldata_length = prepare(len(calldata)//2, "i")
        contract_address = prepare(tx["contractAddress"], "a")
        gas_limit = prepare(tx["gasLimit"], "i")
        tx_bytes = contract_address + gas_limit + calldata_length + calldata.zfill(64)
        byteload += tx_bytes

    return byteload


def bytes2payload(byteload):
    args = [("botId", "s"), 
            ("supplierAddress", "a"), 
            ("blockNumber", "i"), 
            ("gasEstimate", "i"), 
            ("estimatedProfit", "i"), 
            ("profitCurrency", "s")]
    chunks_args = [byteload[i:i+64] for i in range(0, len(args)*64, 64)]
    tx_ln_raw = byteload[len(args)*64: len(args)*64+64]
    tx_ln = int(tx_ln_raw, 16)

    x = len(args)*64+64
    chunks_txs = []
    for _ in range(1, tx_ln+1):
        contract_address = byteload[x:x+64]
        x += 64
        gas_limit = byteload[x:x+64]
        x += 64
        calldata_length = byteload[x:x+64]
        x += 64
        chunks_txs += [contract_address, gas_limit, calldata_length]
        calldata_ln_int = int(calldata_length, 16)*2
        calldata_ln_int = calldata_ln_int if calldata_ln_int > 64 else 64
        calldata = byteload[x:x+calldata_ln_int]
        chunks_txs += [calldata]
        x += calldata_ln_int

    return chunks_args + [tx_ln_raw] + chunks_txs

