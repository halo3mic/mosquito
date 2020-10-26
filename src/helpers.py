from config import *
import time


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
        function = "swapExactTokensForTokensSupportingFeeOnTransferTokens"
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





if __name__=="__main__":
    provider = NODE_INFO["infura"]["html_path"]
    w3 = Web3(Web3.HTTPProvider(provider))
    
    input_amount = 4000
    to_address = "0xddbE1dFC668233bb882014838DAE50deF5Ea967c"
    pool_address = "0xddbE1dFC668233bb882014838DAE50deF5Ea967c"
    path = ["0x404A03728Afd06fB934e4b6f0EaF67796912733A", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"]
    
    uni = Uniswap(w3)
    amount_out = uni.get_amount_out(input_amount, pool_address, inverse=1)
    payload = uni.get_payload(input_amount, amount_out, path, 200000, to_address)
    
    print(amount_out)
    print(payload)

    payload = approve_erc20("0x3f382dbd960e3a9bbceae22651e88158d2791550", "0x93eA6ec350Ace7473f7694D43dEC2726a515E31A", 1000000000000000000000000000)
    print(payload)

    transfer_result = "0xa9059cbb000000000000000000000000ec0b879271e4009230427d02a057b595735b2bf9000000000000000000000000000000000000000000000015af1d78b58c400000"
    assert transfer_result == transfer_erc20("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", "0xEC0B879271e4009230427d02A057B595735b2Bf9", 400*10**18)["calldata"]
