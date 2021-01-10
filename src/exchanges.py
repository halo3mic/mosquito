import src.config as cf


class Uniswap:

    fee = 0.003

    def __init__(self, web3):
        self.web3 = web3
        self.router_address = cf.address("uniswapv2_router")
        self.router_contract = web3.eth.contract(address=self.router_address, abi=cf.abi("uniswapv2_router"))
        
    def get_amount_out(self, input_amount, pool_address, inverse=False):
        bal0, bal1, _ = self.get_reserves(pool_address)
        if inverse: bal0, bal1 = bal1, bal0
        amount_out = (1 - bal1/(bal1+input_amount)) * bal0 * (1-self.fee)
        
        return amount_out

    def swapExactTokensForETH(self, amount_in, path, to_address, last_block_timestamp, amount_out_min=0, gas_limit=200000, tkn_slippage=0.01, time_slippage=300):
        function = "swapExactTokensForETH"
        args = [int(amount_in), int(amount_out_min*(1-tkn_slippage)), path, to_address, last_block_timestamp+time_slippage]
        calldata = self.router_contract.encodeABI(fn_name=function, args=args)
        payload = {"contractAddress": self.router_address, 
                   "calldata": calldata,
                   "gasLimit": gas_limit
                  }

        return payload

    def swapExactETHForTokens(self, amount_in, path, to_address, last_block_timestamp, amount_out_min=0, gas_limit=200000, tkn_slippage=0.01, time_slippage=300): 
        function = "swapExactETHForTokens"
        args = [int(amount_out_min*(1-tkn_slippage)), path, to_address, last_block_timestamp+time_slippage]
        calldata = self.router_contract.encodeABI(fn_name=function, args=args)
        payload = {"contractAddress": self.router_address, 
                   "calldata": calldata,
                   "gasLimit": gas_limit, 
                   "value": int(amount_in)
                  }

        return payload

    def get_reserves(self, pool_address):
        pool_contract = self.web3.eth.contract(address=pool_address, abi=cf.abi("uniswapv2_pool"))
        bal0, bal1, last_update = pool_contract.functions.getReserves().call()
        return bal0, bal1, last_update


class SushiSwap(Uniswap):

    fee = 0.003

    def __init__(self, web3):
        self.web3 = web3
        self.router_address = cf.address("sushiswap_router")
        self.router_contract = web3.eth.contract(address=self.router_address, abi=cf.abi("uniswapv2_router"))


class Crypto(Uniswap):

    fee = 0.003

    def __init__(self, web3):
        self.web3 = web3
        self.router_address = cf.address("crypto_router")
        self.router_contract = web3.eth.contract(address=self.router_address, abi=cf.abi("uniswapv2_router"))
