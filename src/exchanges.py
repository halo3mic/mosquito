import src.config as cf


class Uniswap:

    fee = 0.003

    def __init__(self, web3):
        self.web3 = web3
        self.fee = 0.003
        
    def get_amount_out(self, input_amount, pool_address, inverse=False):
        bal0, bal1, _ = self.get_reserves(pool_address)
        if inverse: bal0, bal1 = bal1, bal0
        amount_out = (1 - bal1/(bal1+input_amount)) * bal0 * (1-self.fee)
        
        return amount_out

    def swapExactTokensForETH(self, input_amount, amount_out, path, gas_limit, to_address, tkn_slippage=0.01, time_slippage=300):
        router_address = cf.address("uniswapv2_router02")
        router_contract = self.web3.eth.contract(address=router_address, abi=cf.abi("uniswapv2_router02"))
        function = "swapExactTokensForETH"
        timestamp = self.web3.eth.getBlock('latest')["timestamp"]
        args = [int(input_amount), int(amount_out*(1-tkn_slippage)), path, to_address, timestamp+time_slippage]
        calldata = router_contract.encodeABI(fn_name=function, args=args)
        payload = {"contractAddress": router_address, 
                   "calldata": calldata,
                   "gasLimit": gas_limit
                  }

        return payload

    def get_reserves(self, pool_address):
        pool_contract = self.web3.eth.contract(address=pool_address, abi=cf.abi("uniswapv2"))
        bal0, bal1, last_update = pool_contract.functions.getReserves().call()
        return bal0, bal1, last_update


class SushiSwap:

    fee = 0.003

    def __init__(self, web3):
        self.web3 = web3

    def get_reserves(self, pool_address):
        pool_contract = self.web3.eth.contract(address=pool_address, abi=cf.abi("uniswapv2"))
        bal0, bal1, last_update = pool_contract.functions.getReserves().call()
        return bal0, bal1, last_update
