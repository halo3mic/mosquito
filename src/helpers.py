from src.config import *
import time
import atexit


class Uniswap:


    def __init__(self, web3):
        self.web3 = web3
        self.fee = 0.003
        
    def get_amount_out(self, input_amount, pool_address, inverse=False):
        pool_contract = self.web3.eth.contract(address=pool_address, abi=ABIS["uniswapv2"])
        bal0, bal1, _ = pool_contract.functions.getReserves().call()
        if inverse: bal0, bal1 = bal1, bal0
        bal0 /= 10**18  # This can depend on the token
        bal1 /= 10**18  # This can depend on the token
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

